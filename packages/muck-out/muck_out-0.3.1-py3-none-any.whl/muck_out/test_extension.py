from .extension import muck_out


async def test_muck_out():
    actor = {
        "attachment": [
            {
                "type": "PropertyValue",
                "name": "Author",
                "value": "acct:helge@mymath.rocks",
            },
            {
                "type": "PropertyValue",
                "name": "Source",
                "value": "https://codeberg.org/bovine/roboherd",
            },
            {"type": "PropertyValue", "name": "Frequency", "value": "Every minute"},
        ],
        "published": "2025-09-17T17:02:51.088028",
        "@context": [
            "https://www.w3.org/ns/activitystreams",
            "https://w3id.org/security/v1",
            {
                "PropertyValue": {
                    "@id": "https://schema.org/PropertyValue",
                    "@context": {
                        "value": "https://schema.org/value",
                        "name": "https://schema.org/name",
                    },
                }
            },
        ],
        "publicKey": {
            "id": "http://abel/actor/AFKb0cQunSBv1fC7sWbQYg#legacy-key-1",
            "owner": "http://abel/actor/AFKb0cQunSBv1fC7sWbQYg",
            "publicKeyPem": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEArmnl5tRTKzXoHsOmEPwk\nfC6BY1ZtueThLmXF9BjtIiHSKXvH0cema16EMb6efyHoLBvlAcdvEpP0QR3AKvb/\n48wArzIUnLi3RxOlANhUK+NHOuNJQxcPrnX06rt0MZ5K+3hK1XZQV559vecEyIk+\nxZxlz9KaSDEnsHKbHueNJvhrGV1TdppdCSe5qcml/Pkc3yIG9gq2aKx7XLIPORHe\nDRqJUpLyUX5XiOOGLHVUuKz3U87+ZWxK+GjHB46hMl+W4clJNLedxY81eGCeGoOV\ni6qEHRuWC68Q1IhexIXyujlBBHAOqgLRO/VNpg6anOZWDX/s6EvsQq4BBPNI3HZe\newIDAQAB\n-----END PUBLIC KEY-----\n",
        },
        "id": "http://abel/actor/AFKb0cQunSBv1fC7sWbQYg",
        "type": "Service",
        "inbox": "http://abel/inbox/3c2TKngdcWGJOj4j3ALC1g",
        "outbox": "http://abel/outbox/vCJcPoNbwkNlJU9o7O8qDA",
        "followers": "http://abel/followers/RKsezXFc1SGvQKvucioJxg",
        "following": "http://abel/following/CLwJywMuHXFIyPEz9sRBhg",
        "preferredUsername": "kitty",
        "name": "The kitty",
        "summary": "I'm a kitty.",
        "icon": {
            "mediaType": "image/png",
            "type": "Image",
            "url": "https://dev.bovine.social/assets/bull-horns.png",
        },
        "identifiers": ["acct:kitty@abel", "http://abel/actor/AFKb0cQunSBv1fC7sWbQYg"],
        "endpoints": {"sharedInbox": "http://abel/shared_inbox"},
    }

    result = await muck_out({"raw": actor})

    assert "parsed" in result
