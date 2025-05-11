from routers.friend import get_all_social_distance
from routers.post import post_recommendations

print(get_all_social_distance(1))
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzQ2OTgwMTM0fQ.okUMcufqbZBnLPSewzZw_Ru9IJDKsgUZjUjVPfxZ6lA"
print(post_recommendations(1, token))
# print(123)