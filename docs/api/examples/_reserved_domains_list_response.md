<!-- Code generated for API Clients. DO NOT EDIT. -->

#### Example Response

```json
{
	"next_page_uri": null,
	"reserved_domains": [
		{
			"acme_challenge_cname_target": null,
			"certificate": null,
			"certificate_management_policy": {
				"authority": "letsencrypt",
				"private_key_type": "ecdsa"
			},
			"certificate_management_status": {
				"provisioning_job": {
					"error_code": null,
					"msg": "Managed certificate provisioning in progress.",
					"retries_at": null,
					"started_at": "2025-01-09T10:06:31Z"
				},
				"renews_at": null
			},
			"cname_target": "4knqktdwka2umyjjc.2tv3s7fnuksuohtmm.local-ngrok-cname.com",
			"created_at": "2025-01-09T10:06:30Z",
			"description": "Device 0001 Dashboard",
			"domain": "manage-0002.app.example.com",
			"error_redirect_url": null,
			"http_endpoint_configuration": null,
			"https_endpoint_configuration": null,
			"id": "rd_2rO5HKcS41R2J2VErmyTT9WBmR7",
			"metadata": "{\"service\": \"dashboard\"}",
			"region": "",
			"uri": "https://api.ngrok.com/reserved_domains/rd_2rO5HKcS41R2J2VErmyTT9WBmR7"
		},
		{
			"acme_challenge_cname_target": null,
			"certificate": {
				"id": "cert_2rO5HAohCY7BB4lKK1oSv3i4OEX",
				"uri": "https://api.ngrok.com/tls_certificates/cert_2rO5HAohCY7BB4lKK1oSv3i4OEX"
			},
			"certificate_management_policy": null,
			"certificate_management_status": null,
			"cname_target": "2udamkamcl8pjmrff.2tv3s7fnuksuohtmm.local-ngrok-cname.com",
			"created_at": "2025-01-09T10:06:30Z",
			"domain": "myapp.mydomain.com",
			"error_redirect_url": null,
			"http_endpoint_configuration": null,
			"https_endpoint_configuration": null,
			"id": "rd_2rO5HEj4XkVczjoEqPOyLnTdQ5s",
			"region": "",
			"uri": "https://api.ngrok.com/reserved_domains/rd_2rO5HEj4XkVczjoEqPOyLnTdQ5s"
		}
	],
	"uri": "https://api.ngrok.com/reserved_domains"
}
```
