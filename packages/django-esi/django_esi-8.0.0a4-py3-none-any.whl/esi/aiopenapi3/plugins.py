from aiopenapi3.plugin import Document, Init

class Trim204ContentType(Document):
    """
    Removes and content-type from responses on a 204 reponses
    A 204 never has content...
    """
    def parsed(self, ctx: Document.Context) -> Document.Context:
        spec = ctx.document
        # Patch all paths
        for path_item in spec.get("paths", {}).values():
            for method_name in ("get", "post", "put", "delete", "patch", "options", "head"):
                method = path_item.get(method_name)
                if not method:
                    continue
                if "204" in method['responses']:
                    method['responses']["204"].pop("content", [])
        return ctx


class Add304ContentType(Document):
    """
    Adds 304 content-type to responses
    A 304 never has content. ESI defualt has application/json
    This is a hack for now
    """
    def parsed(self, ctx: Document.Context) -> Document.Context:
        spec = ctx.document
        # Patch all paths
        for path_item in spec.get("paths", {}).values():
            for method_name in ("get", "post", "put", "delete", "patch", "options", "head"):
                method = path_item.get(method_name)
                if not method:
                    continue
                if "304" not in method['responses']:
                    method['responses']["304"]={
                        "description": "Not Modified"
                    }
        return ctx


class RemoveSecurityParameter(Document):
    """
    Removes the whole OAuth2 securityScheme
    """
    def parsed(self, ctx: Document.Context) -> Document.Context:
        print("RemoveSecurityParameterPlugin: Removing OAuth2 securityScheme")
        spec = ctx.document
        oauth2 = spec.get("components", {}).get("securitySchemes", {}).pop("OAuth2", None)
        # Patch all paths
        for path_item in spec.get("paths", {}).values():
            for method_name in ("get", "post", "put", "delete", "patch", "options", "head"):
                method = path_item.get(method_name)
                if not method:
                    continue
                method.pop("security", None)

        return ctx


class TrimSecurityParameter(Document):
    """TrimSecurityParameter
    Trims out of Spec OAuth2 attributes. CCP have fixed this.
    Leaving in place in case we need a quick reference again.
    """
    def parsed(self, ctx: Document.Context) -> Document.Context:
        print("TrimSecurityParameter: Trimming out of spec attributes")
        spec = ctx.document
        oauth2 = spec.get("components", {}).get("securitySchemes", {}).get("OAuth2")
        if oauth2 and oauth2.get("type") == "oauth2":
            oauth2.pop("in", None)
            oauth2.pop("name", None)
        return ctx


class PatchCompatibilityDatePlugin(Document):
    """
    Makes the X-Compatibility-Date header optional

    This is because WE specifically add it in the library to the HTTP requests,
    but without this, it will be a required parameter during request generation before it hits the HTTP library.
    """
    def parsed(self, ctx: Document.Context) -> Document.Context:
        print("PatchCompatibilityDatePlugin: making compatibility date optional")
        spec = ctx.document

        def patch_param(param):
            # Follow $ref if present
            if "$ref" in param:
                ref = param["$ref"]
                parts = ref.split("/")
                if parts[1] == "components" and parts[2] == "parameters":
                    param_name = parts[-1]
                    comp_param = spec.get("components", {}).get("parameters", {}).get(param_name)
                    if comp_param and comp_param.get("name") == "X-Compatibility-Date":
                        comp_param["required"] = False
            else:
                # Inline parameter
                if (param.get("name") == "X-Compatibility-Date" and param.get("in") == "header"):
                    param["required"] = False

        # Patch all paths
        for path_item in spec.get("paths", {}).values():
            for method_name in ("get", "post", "put", "delete", "patch", "options", "head"):
                method = path_item.get(method_name)
                if not method:
                    continue
                for param in method.get("parameters", []):
                    patch_param(param)

        # Patch global parameters in components
        for param_name, param in spec.get("components", {}).get("parameters", {}).items():
            if param.get("name") == "X-Compatibility-Date" and param.get("in") == "header":
                param["required"] = False

        return ctx


class DjangoESIInit(Init):

    def __init__(self, ua_appname):
        super().__init__()
        self.app_name = ua_appname

    def initialized(self, ctx: Init.Context) -> Init.Context:
        # Force the app_name into the api client class for etags
        self.api.app_name=self.app_name
        return ctx  # noqa
