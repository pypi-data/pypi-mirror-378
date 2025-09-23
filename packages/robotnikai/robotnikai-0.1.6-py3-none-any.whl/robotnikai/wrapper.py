import json
import logging
import os
import uuid
from dataclasses import dataclass
from typing import Any, List, Literal, Optional, Tuple, Union

import robotnikai
import requests
from dotenv import load_dotenv

try:
    import redis
except ImportError:
    redis = None

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

load_dotenv()

DEFAULT_HOST = "https://robotnikai.com"


@dataclass
class ApiResponse:
    status_code: int
    text: str
    headers: dict
    url: str
    ok: bool


def retrieve_app_id():
    env_app_id = os.environ.get("APP_ID")
    env_org_slug = os.environ.get("ORG_SLUG")
    env_app_slug = os.environ.get("APP_SLUG")
    if env_app_id:
        try:
            return int(env_app_id)
        except ValueError:
            return str(env_app_id)
    elif env_org_slug and env_app_slug:
        return f"{env_org_slug}/{env_app_slug}"


class IntegrationsApi(
    robotnikai.IntegrationsApi,
    robotnikai.IntegrationsAPICallsApi,
):
    def __init__(self, api_client=None):
        super().__init__(api_client)
        self.connection_id = os.environ.get("CONNECTION_ID", None)
        self._initial_connection_set = self.connection_id is not None
        if not self.connection_id:
            logger.warning(
                "CONNECTION_ID environment variable is not set. Defaulting to None."
            )
        else:
            logger.info(f"Using CONNECTION_ID: {self.connection_id}")

    def call(
        self,
        integration: robotnikai.Integration,
        method: str = None,
        endpoint: str = None,
        connection_id=None,
        *args,
        **kwargs,
    ) -> Tuple[dict, ApiResponse]:
        # Make the request directly to the call endpoint
        api_url = f'{os.getenv("API_BASE_URL", DEFAULT_HOST).rstrip("/")}/api/integrations/{integration.integration_id}/call/'

        response = requests.post(
            api_url,
            params={"connection_id": connection_id},
            json={
                "method": method,
                "endpoint": endpoint,
                "data": kwargs.get("data", kwargs.get("json", {})),
                "request_headers": kwargs.get("headers", {}),
                "request_params": kwargs.pop("params", {}),
            },
            headers={
                "Authorization": "App-Token {}".format(os.environ.get("APP_TOKEN")),
                "Content-Type": "application/json",
            },
        )

        try:
            api_response = None
            response_data = response.json()
            if "api_response" in response_data:
                api_response = ApiResponse(
                    status_code=response_data["api_response"]["status_code"],
                    text=response_data["api_response"]["text"],
                    headers=response_data["api_response"]["headers"],
                    url=response_data["api_response"]["url"],
                    ok=response_data["api_response"]["ok"],
                )
        except json.JSONDecodeError:
            # If the response is not JSON, create a generic ApiResponse
            api_response = ApiResponse(
                status_code=response.status_code,
                text=response.text,
                headers=dict(response.headers),
                url=response.url,
                ok=response.ok,
            )

        try:
            if not response.ok:
                raise Exception(response.text)
            api_data = response_data.get("api_data", {})
            if not self._initial_connection_set and "connection_id" in response_data:
                self.connection_id = response_data["connection_id"]
            return api_data, api_response
        except Exception as e:
            if not api_response:
                logger.error(f"Error in API call: {str(e)}")
                raise e
            return None, api_response

    def _format_responses(self, responses):
        full_response = []
        for r in responses:
            if "api_response" in r:
                api_response = ApiResponse(
                    status_code=r["api_response"]["status_code"],
                    text=r["api_response"]["text"],
                    headers=r["api_response"]["headers"],
                    url=r["api_response"]["url"],
                    ok=r["api_response"]["ok"],
                )
            else:
                api_response = None
            try:
                api_data = r.get("api_data", {})
                full_response.append((api_data, api_response))
            except Exception as e:
                logger.error(f"Error processing response: {str(e)}")
                full_response.append((None, api_response))
        return full_response

    def parallel_call_stream(
        self,
        integration: robotnikai.Integration,
        method,
        endpoint,
        data_list,
        connection_id=None,
        *args,
        **kwargs,
    ):
        """
        Generator method for streaming parallel calls.
        Yields individual responses as they become available.

        Yields:
            dict: Individual response data with keys: index, response, completed, total
        """

        payload = {
            "method": method,
            "endpoint": endpoint,
            "data_list": data_list,
            "request_headers": kwargs.get("headers", {}),
            "request_params": kwargs.pop("params", {}),
            "streaming": True,
        }

        # Make the request directly to the parallel_call endpoint
        api_url = f'{os.getenv("API_BASE_URL", DEFAULT_HOST).rstrip("/")}/api/integrations/{integration.integration_id}/parallel_call/'

        response = requests.post(
            api_url,
            params={"connection_id": connection_id},
            json=payload,
            headers={
                "Authorization": "App-Token {}".format(os.environ.get("APP_TOKEN")),
                "Content-Type": "application/json",
            },
            stream=True,
            timeout=300,  # Longer timeout for streaming
        )

        if not response.status_code in [200, 201, 202, 204]:
            raise Exception(response.text)

        # Parse streaming response and yield individual results
        for line in response.iter_lines(decode_unicode=True):
            if line.startswith("data: "):
                try:
                    data = json.loads(line[6:])  # Remove 'data: ' prefix
                    # Set connection_id when available
                    if not self._initial_connection_set and data.get("connection_id"):
                        self.connection_id = data["connection_id"]

                    if data.get("completed") is True:
                        # Final completion message - yield and break
                        yield {
                            "final": True,
                            "total_processed": data.get("total_processed"),
                        }
                        break
                    else:
                        api_data = data["response"]["api_data"]
                        api_response = ApiResponse(
                            status_code=data["response"]["api_response"]["status_code"],
                            text=data["response"]["api_response"]["text"],
                            headers=data["response"]["api_response"]["headers"],
                            url=data["response"]["api_response"]["url"],
                            ok=data["response"]["api_response"]["ok"],
                        )
                        # Individual response - yield it
                        yield {
                            "data": api_data,
                            "response": api_response,
                            "index": data.get("index"),
                            "total": data.get("total"),
                        }
                except json.JSONDecodeError:
                    continue

    def parallel_call(
        self,
        integration: robotnikai.Integration,
        method,
        endpoint,
        data_list,
        connection_id=None,
        *args,
        **kwargs,
    ) -> Tuple[dict, ApiResponse]:
        response = self.invoke_parallel_call_with_http_info(
            integration.integration_id,
            invoke_parallel_call_request=robotnikai.InvokeParallelCallRequest(
                method=method,
                endpoint=endpoint,
                data_list=data_list,
                request_headers=kwargs.get("headers", {}),
                streaming=False,
            ),
        )

        full_response = self._format_responses(response.data.responses)

        if not self._initial_connection_set and response.data.connection_id:
            self.connection_id = response.data.connection_id
        return full_response


class CacheApi:
    def __init__(self, cache_config=None):
        # Use shared cache configuration
        self.cache_service_url = cache_config["cache_service_url"]
        self.task_id = cache_config["task_id"]
        self.session = cache_config["session"]
        self.redis_client = cache_config["redis_client"]

    def _get_redis_key(self, key: str) -> str:
        """Generate Redis key with proper namespacing - to be overridden by subclasses"""
        raise NotImplementedError("Subclasses must implement _get_redis_key")

    def _get_base_params(self) -> dict:
        """Get base parameters for HTTP cache service - to be overridden by subclasses"""
        raise NotImplementedError("Subclasses must implement _get_base_params")

    def _get_set_payload(self, key: str, value: Any, ttl: Optional[int] = None) -> dict:
        """Get payload for HTTP cache service set operation - to be overridden by subclasses"""
        return {"key": key, "value": value, "ttl": ttl}

    def get(self, key: str) -> Any:
        """Get cached value by key"""
        if self.cache_service_url:
            # Use HTTP cache service
            try:
                response = self.session.get(
                    f"{self.cache_service_url}/get/{key}/",
                    params=self._get_base_params(),
                )
                return response.json()
            except Exception as e:
                logger.error(f"Error getting cache for key {key}: {str(e)}")
                return None
        else:
            # Use Redis directly
            try:
                redis_key = self._get_redis_key(key)
                value = self.redis_client.get(redis_key)
                if value is None:
                    return None
                return {
                    "key": key,
                    "value": value,
                    "exists": True,
                    "ttl": self.redis_client.ttl(redis_key),
                }
            except Exception as e:
                logger.error(f"Error getting cache for key {key}: {str(e)}")
                return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set cached value by key"""
        if self.cache_service_url:
            # Use HTTP cache service
            try:
                response = self.session.post(
                    f"{self.cache_service_url}/set/",
                    params=self._get_base_params(),
                    json=self._get_set_payload(key, value, ttl),
                )
                return response.json()
            except Exception as e:
                logger.error(f"Error setting cache for key {key}: {str(e)}")
                return False
        else:
            # Use Redis directly
            try:
                redis_key = self._get_redis_key(key)
                serialized_value = json.dumps(value)
                if ttl:
                    self.redis_client.setex(redis_key, ttl, serialized_value)
                else:
                    self.redis_client.set(redis_key, serialized_value)
                return {
                    "success": True,
                    "key": key,
                    "message": "Cache set successfully",
                    "ttl": ttl,
                }
            except Exception as e:
                logger.error(f"Error setting cache for key {key}: {str(e)}")
                return False

    def delete(self, key: str) -> bool:
        """Delete cached value by key"""
        if self.cache_service_url:
            # Use HTTP cache service
            try:
                response = self.session.delete(
                    f"{self.cache_service_url}/delete/{key}/",
                    params=self._get_base_params(),
                )
                return response.json()
            except Exception as e:
                logger.error(f"Error deleting cache for key {key}: {str(e)}")
                return False
        else:
            # Use Redis directly
            try:
                redis_key = self._get_redis_key(key)
                deleted_count = self.redis_client.delete(redis_key)
                message = (
                    "Key deleted successfully" if deleted_count > 0 else "Key not found"
                )
                return {
                    "success": True,
                    "message": message,
                    "key": key,
                    "deleted": deleted_count > 0,
                }
            except Exception as e:
                logger.error(f"Error deleting cache for key {key}: {str(e)}")
                return False


class AppCacheApi(CacheApi):
    def __init__(self, cache_config=None):
        super().__init__(cache_config)
        self.action_id = os.environ.get("ACTION_ID")
        self.app_id = retrieve_app_id()

    def _get_redis_key(self, key: str) -> str:
        """Generate Redis key with proper namespacing"""
        return f"app:{self.app_id}:{key}"

    def _get_base_params(self) -> dict:
        """Get base parameters for HTTP cache service"""
        return {
            "task_id": self.task_id,
            "action_id": self.action_id,
            "cache_type": "app",
        }

    def _get_set_payload(self, key: str, value: Any, ttl: Optional[int] = None) -> dict:
        """Get payload for HTTP cache service set operation"""
        return {
            "action": self.action_id,
            "key": key,
            "value": value,
            "ttl": ttl,
        }


class UserCacheApi(CacheApi):
    def __init__(self, cache_config=None):
        super().__init__(cache_config)

    def _get_redis_key(self, key: str) -> str:
        """Generate Redis key with proper namespacing"""
        return f"org:{self.task_id}:{key}"

    def _get_base_params(self) -> dict:
        """Get base parameters for HTTP cache service"""
        return {
            "task_id": self.task_id,
            "cache_type": "org",
        }


class GraphqlException(Exception):
    """Custom exception for GraphQL errors."""


class TablesApi(
    robotnikai.ApplicationsTablesGraphQLApi,
):
    def __init__(
        self, client: robotnikai.ApiClient, integrations_api: "IntegrationsApi"
    ):
        super().__init__(client)
        self.client = client
        self.integrations_api = integrations_api

    def graphql(
        self,
        table: str,
        query: str = None,
        variables: dict = None,
        graph_ql_request: robotnikai.GraphQLRequest = None,
    ) -> Any:
        app_id = retrieve_app_id()

        if not app_id:
            raise ValueError("APP_ID variable is not set")

        if not graph_ql_request:
            if not query or not variables:
                raise ValueError("Either query or variables must be provided")
            graph_ql_request = robotnikai.GraphQLRequest(
                query=query, variables=variables
            )

        # Automatically inject connection_id from integrations API if available
        if self.integrations_api.connection_id:
            if graph_ql_request.variables is None:
                graph_ql_request.variables = {}

            # Only inject if connection_id is not already present
            if "connection_id" not in graph_ql_request.variables:
                graph_ql_request.variables["connection_id"] = (
                    self.integrations_api.connection_id
                )
                logger.info(
                    f"Auto-injected connection_id ({self.integrations_api.connection_id}) to graphql variables"
                )

        try:
            response = self.apps_graphql_query(
                app=app_id,
                table=table,
                graph_ql_request=graph_ql_request,  # type: ignore
            )
            if response.errors and len(response.errors) > 0:
                raise GraphqlException("GraphQL errors occurred", response.errors)
            return response
        except Exception as e:
            raise e


class Task(CacheApi):
    def __init__(self, cache_config=None):
        super().__init__(cache_config)

    def set_progress(
        self,
        progress: int,
        info: str,
        status: Literal["pending", "completed", "failed"] = "pending",
    ):
        """
        Set the progress of the current task.

        Parameters:
            progress (int): Progress percentage (0-100)
            info (str): Additional information about the task
            status (str): Status of the task (e.g., 'pending', 'completed', 'failed')
        """
        if not self.task_id:
            logger.error("TASK_ID variable is not set")
            return

        if self.cache_service_url:
            # Use HTTP cache service
            try:
                response = self.session.post(
                    f"{self.cache_service_url}/set-progress/{self.task_id}/",
                    json={
                        "progress": progress,
                        "info": info,
                        "status": status,
                    },
                )
                return response.json()
            except Exception as e:
                logger.error(
                    f"Error setting progress for task {self.task_id}: {str(e)}"
                )
                return None
        else:
            # Use Redis directly - store progress info
            try:
                progress_key = f"task:progress:{self.task_id}"
                progress_data = {
                    "progress": progress,
                    "info": info,
                    "status": status,
                    "updated_at": str(uuid.uuid4()),  # Using uuid as simple timestamp
                }
                self.redis_client.set(progress_key, json.dumps(progress_data))
                logger.info(f"Task {self.task_id} progress set to {progress}%: {info}")
                return {
                    "success": True,
                    "message": "Progress updated successfully",
                    "task_id": self.task_id,
                    "progress": int(progress),
                    "info": info,
                    "status": status,
                }
            except Exception as e:
                logger.error(
                    f"Error setting progress for task {self.task_id}: {str(e)}"
                )
                return None


class PluginsApi(robotnikai.PluginInterfacesPluginsApi, robotnikai.PluginsApi):
    def __init__(self, api_client=None):
        super().__init__(api_client)

    def invoke(
        self,
        plugin: str,
        integration: str,
        connection_ids: List[Union[str, int]] = [],
        **payload,
    ) -> Any:
        namespace, capability = plugin.split(".")
        logger.info(
            f"Invoking plugin: {namespace}.{capability} with integration: {integration}"
        )

        try:
            # Import plugin module
            module_name = f"plugins.{namespace}_{integration}"
            module = __import__(module_name, fromlist=[capability])

            # Get the capability function from the module
            capability_func = getattr(module, capability)

            # Invoke the capability function
            return capability_func(connection_ids=connection_ids, **payload)
        except ImportError as e:
            logger.error(f"Failed to import module {module_name}: {e}")
            raise ImportError(f"Plugin module '{module_name}' not found")
        except AttributeError as e:
            logger.error(
                f"Capability '{capability}' not found in module {module_name}: {e}"
            )
            raise AttributeError(
                f"Capability '{capability}' not implemented in plugin '{namespace}_{integration}'"
            )
        except NotImplementedError as e:
            logger.error(
                f"Capability '{capability}' in plugin '{namespace}_{integration}' is not implemented"
            )
        except Exception as e:
            logger.error(f"Error invoking capability '{capability}': {e}")
            raise


class API:
    def __init__(self):
        # Initialize shared cache configuration once
        self._cache_config = self._init_cache_config()

        self._client = robotnikai.ApiClient(self.configuration)
        self.integrations = IntegrationsApi(self._client)
        self.plugins = PluginsApi(self._client)
        self.tables = TablesApi(self._client, self.integrations)
        self.app_cache = AppCacheApi(self._cache_config)
        self.user_cache = UserCacheApi(self._cache_config)
        self.task = Task(self._cache_config)

    def _init_cache_config(self):
        """Initialize cache configuration once and share across all cache instances"""
        cache_service_url = os.getenv("CACHE_SERVICE_URL")
        task_id = str(os.environ.get("TASK_ID", uuid.uuid4()))

        if cache_service_url:
            # Use HTTP cache service
            session = requests.Session()
            cache_service_token = os.environ.get("CACHE_SERVICE_TOKEN")
            session.headers.update(
                {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {cache_service_token}",
                }
            )
            redis_client = None
            logger.info(
                f"Using HTTP cache service at {cache_service_url} with task ID {task_id}"
            )
        else:
            session = None
            # Use direct Redis connection
            if redis is None:
                raise ImportError(
                    "Redis library is not installed. Please install it with: pip install redis"
                )

            redis_host = os.getenv("REDIS_HOST", "localhost")
            redis_port = int(os.getenv("REDIS_PORT", 6379))
            redis_db = int(os.getenv("REDIS_DB", 0))
            redis_password = os.getenv("REDIS_PASSWORD")

            try:
                redis_client = redis.Redis(
                    host=redis_host,
                    port=redis_port,
                    db=redis_db,
                    password=redis_password,
                    decode_responses=True,
                )
                # Test the connection
                redis_client.ping()
                logger.info(
                    f"Using Redis cache at {redis_host}:{redis_port}/{redis_db} with task ID {task_id}"
                )
            except redis.ConnectionError as e:
                raise ConnectionError(
                    f"Failed to connect to Redis at {redis_host}:{redis_port}/{redis_db}. "
                    f"Please ensure Redis is running and accessible. Error: {str(e)}"
                )
            except redis.AuthenticationError as e:
                raise ConnectionError(
                    f"Failed to authenticate with Redis at {redis_host}:{redis_port}/{redis_db}. "
                    f"Please check your REDIS_PASSWORD. Error: {str(e)}"
                )
            except Exception as e:
                raise ConnectionError(
                    f"Failed to initialize Redis connection at {redis_host}:{redis_port}/{redis_db}. "
                    f"Error: {str(e)}"
                )

        return {
            "cache_service_url": cache_service_url,
            "task_id": task_id,
            "session": session,
            "redis_client": redis_client,
        }

    @property
    def configuration(self):
        configuration = robotnikai.Configuration()
        configuration.host = os.getenv("API_BASE_URL", DEFAULT_HOST)
        configuration.api_key["knoxApiToken"] = "App-Token {}".format(
            os.environ.get("APP_TOKEN")
        )
        return configuration

    def close(self):
        self._client.close()

    def notify_me(self, subject: str, text: Optional[str], html: Optional[str] = None):
        """
        Send a notification to the user.

        Parameters:
            subject (str): Subject of the notification
            text (Optional[str]): Text content of the notification
            html (Optional[str]): HTML content of the notification
        """
        if not text and not html:
            raise ValueError("At least one of 'text' or 'html' must be provided")

        response = requests.post(
            f"{self.configuration.host}/api/integrations/mailer/notify-me/",
            json={
                "subject": subject,
                "text": text,
                "html": html,
            },
            headers={
                "Authorization": self.configuration.api_key["knoxApiToken"],
                "Content-Type": "application/json",
            },
        )
        return response.json() if response.ok else response.text
