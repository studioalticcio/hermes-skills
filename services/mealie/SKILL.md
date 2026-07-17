---
name: mealie
description: Manage the Mealie recipe manager via its REST API (list/search recipes, scrape from URL, meal plans).
version: 1.0.0
platforms: [linux]
tags: [hermes, services, mealie, recipes, cooking]
---

# Mealie

Mealie recipe manager runs locally at `http://localhost:<PORT>`.

## Setup (API token)

No token in env. Generate one in the Mealie UI:
**User Settings > API Tokens > Create** (or `Settings > API Tokens`). Add it to secrets:

```
echo 'MEALIE_API_TOKEN=<token>' >> /var/lib/hermes/secrets/services.env
```

Auth header: `Authorization: Bearer $MEALIE_API_TOKEN`

```bash
set -a; . /var/lib/hermes/secrets/services.env; set +a
B="http://localhost:<PORT>/api"
H="Authorization: Bearer $MEALIE_API_TOKEN"
```

## Commands

```bash
# List recipes (paginated)
curl -s "$B/recipes?perPage=50" -H "$H" | python3 -c "import json,sys; [print(r['slug'], '-', r['name']) for r in json.load(sys.stdin)['items']]"

# Search recipes
curl -s "$B/recipes?search=QUERY" -H "$H" | python3 -c "import json,sys; [print(r['slug'], '-', r['name']) for r in json.load(sys.stdin)['items']]"

# Get a recipe by slug
curl -s "$B/recipes/RECIPE_SLUG" -H "$H"

# Add a recipe from a URL (Mealie scrapes it)
curl -s -X POST "$B/recipes/create/url" -H "$H" -H "Content-Type: application/json" \
  -d '{"url":"https://example.com/some-recipe","includeTags":true}'
# returns the new recipe slug

# Create a meal plan entry (date YYYY-MM-DD; entryType: breakfast|lunch|dinner|side)
curl -s -X POST "$B/households/mealplans" -H "$H" -H "Content-Type: application/json" \
  -d '{"date":"2026-06-25","entryType":"dinner","recipeId":"RECIPE_ID"}'
# On older Mealie: POST /api/groups/mealplans

# This week's meal plan
curl -s "$B/households/mealplans/today" -H "$H"
```

## Notes

- All commands are local.
- Meal-plan endpoint path differs by version (`households` vs `groups`); try households first.
