def calculate_sleep_duration(response):
    # Shopify returns rate limit information in the response headers
    # Example headers: 'X-Shopify-Shop-Api-Call-Limit': '32/40'
    rate_limit = response.headers.get("X-Shopify-Shop-Api-Call-Limit", "").decode("utf-8")
    if rate_limit:
        current, maximum = map(int, rate_limit.split("/"))
        # Calculate sleep duration based on how close you are to the limit
        if current > maximum * 0.8:  # If usage is over 80% of the limit
            return (maximum - current) / (maximum * 0.2) * 2  # Increase sleep time
        else:
            return 0  # Minimum sleep to avoid hitting the server too quickly
    return 1  # Default sleep if no rate limit info is available
