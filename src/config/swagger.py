template = {
    "swagger": "2.0",
    "info": {
        "title": "Unified API Server",
        "description": "API for obtaining shipping rates from various courier services.",
        "contact": {
            "responsibleOrganization": "",
            "responsibleDeveloper": "",
            "email": "tbannaarr@gmail.com",
            "url": "www.github.com/bannaarr01",
        },
        "termsOfService": "www.github.com/bannaarr01",
        "version": "1.0"
    },
    "basePath": "/api/v1", #baseP for blueprint reg, so all follows
    "schemes": [
        "http",
        "https"
    ],
    "securityDefinitions": {
        "Bearer": { #using bearer auth
            "type": "apiKey",
            "name": "Authorization", #send this
            "in": "header", #in the header
            "description": "JWT Authorization header using the Bearer scheme. Example: \"Authorization: Bearer {token}\""
        }
    },
}

swagger_config = {
    "headers": [ #initial headers
    ],
    "specs": [
        {#should be compatible with data doc tools, e.g openAPI
            "endpoint": 'apispec',
            "route": '/apispec.json',#get json version of the doc
            "rule_filter": lambda rule: True,  # all in
            "model_filter": lambda tag: True,  # all in
        }
    ],
    "static_url_path": "/flasgger_static",# d css shown on d doc
    "swagger_ui": True,
    "specs_route": "/" #show doc at homePage
}
