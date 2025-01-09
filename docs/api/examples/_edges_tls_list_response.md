<!-- Code generated for API Clients. DO NOT EDIT. -->

#### Example Response

```json
{
	"next_page_uri": null,
	"tls_edges": [
		{
			"backend": null,
			"created_at": "2025-01-09T10:06:58Z",
			"description": "acme tls edge",
			"hostports": ["example.com:443"],
			"id": "edgtls_2rO5Kinq48wd7m7CO8vHDI6Ty8j",
			"ip_restriction": null,
			"metadata": "{\"environment\": \"staging\"}",
			"mutual_tls": null,
			"policy": null,
			"tls_termination": null,
			"traffic_policy": null,
			"uri": "https://api.ngrok.com/edges/tls/edgtls_2rO5Kinq48wd7m7CO8vHDI6Ty8j"
		},
		{
			"backend": {
				"backend": {
					"id": "bkdhr_2rO5JDOZ5ZOwQPYipWrgWrPzgxy",
					"uri": "https://api.ngrok.com/backends/http_response/bkdhr_2rO5JDOZ5ZOwQPYipWrgWrPzgxy"
				},
				"enabled": true
			},
			"created_at": "2025-01-09T10:06:46Z",
			"description": "acme tls edge",
			"hostports": ["endpoint-example2.com:443"],
			"id": "edgtls_2rO5JBpHlprUyUD5xqrLwoI7dak",
			"ip_restriction": null,
			"mutual_tls": null,
			"policy": null,
			"tls_termination": null,
			"traffic_policy": null,
			"uri": "https://api.ngrok.com/edges/tls/edgtls_2rO5JBpHlprUyUD5xqrLwoI7dak"
		}
	],
	"uri": "https://api.ngrok.com/edges/tls"
}
```
