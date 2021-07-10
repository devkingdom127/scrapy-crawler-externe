# Worker administrative documents crawler

### 1.1.1

- Handling post endpoint.
- Handle json content types.
- Add extensions.

### 1.1.0

- Handling redirect: when a website is redirected, we now follow the link.
- Do not allow go to another domain and limit size download 
- Add more accepted content types
- Handle more links, with better javascript pattern, handling of frame.
- All configuration (denied pattern, allowed CDN etc.) is now defined in an external file stored on AWS 
(`crawler_deny_config.json`).

### 1.0.0

First version 

