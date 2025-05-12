from routers.friend import get_all_social_distance
from routers.post import post_recommendations
from routers.media import get_media, add_media, delete_media, update_media
from models import Media

# print(get_all_social_distance(1))
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzQ3MDU1OTY0fQ.BJDpVdItAa_Hocfogmv20KYVl6Sayl-6eMq_zgAErwE"
# print(post_recommendations(1, token))
# print(123)

with open("/Users/shunhanglo/Documents/Programming/IERG4210/images/azure1.png", "rb") as f:
    f = f.read()
    b = bytes(f)
    print(add_media(b, token))

# with open("/Users/shunhanglo/Documents/Programming/IERG4210/images/cart1.png", "rb") as f:
#     f = f.read()
#     b = bytes(f)
#     update_media(Media(media_id=3, userid=1, image_data=b), token)

# print(delete_media(3, token))

