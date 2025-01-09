<!-- Code generated for API Clients. DO NOT EDIT. -->

#### Example Response

```json
{
	"event_subscriptions": [
		{
			"created_at": "2025-01-09T10:06:54Z",
			"description": "ip policy creations",
			"destinations": [
				{
					"id": "ed_2rO5KG46OcoPzQbrGodGOylHtAi",
					"uri": "https://api.ngrok.com/event_destinations/ed_2rO5KG46OcoPzQbrGodGOylHtAi"
				}
			],
			"id": "esb_2rO5KB7saTnudh7dx47leBT3qbI",
			"metadata": "{\"environment\": \"staging\"}",
			"sources": [
				{
					"type": "ip_policy_created.v0",
					"uri": "https://api.ngrok.com/event_subscriptions/esb_2rO5KB7saTnudh7dx47leBT3qbI/sources/ip_policy_created.v0"
				}
			],
			"uri": "https://api.ngrok.com/event_subscriptions/esb_2rO5KB7saTnudh7dx47leBT3qbI"
		}
	],
	"next_page_uri": null,
	"uri": "https://api.ngrok.com/event_subscriptions"
}
```
