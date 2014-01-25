from pymongo import MongoClient, GEO2D
import cfg

client = MongoClient(cfg.DB_CONF["host"], cfg.DB_CONF["port"]).watson


class DBConnector():
    def __init__(self):
        pass

    def add_user(self, external_id, session_key):

        cursor = client.users.find({"external_id": external_id})
        if cursor.count() > 0:
            return client.users.update({
                                           "external_id": external_id}, {
                                           "$set": {"session_key": session_key}
                                       })
        else:
            return client.users.insert({
                "external_id": external_id,
                "session_key": session_key,
                "cursor": None
            })

    def update_cursor(self, user_id, cursor):
        client.users.update({"_id": user_id},
                            {"$set": {"cursor": cursor}})

    def delete_user(self, user_id):
        client.users.remove({"_id": user_id})

    def get_user(self, external_id):
        return client.users.find({"external_id": external_id})

    def get_all_users(self):
        return client.users.find({})

    def upsert_image(self, user_id, filename, coords, external_ref, hash):
        client.images.ensure_index([("geo", GEO2D)])
        id = client.images.insert({
                                      "user_id": user_id,
                                      "filename": filename,
                                      "geo": coords,
                                      "external_ref": external_ref,
                                      "hash": hash
                                  }, upsert=True)
        return id

    def get_image(self, user_id=None, hash=None):
        if user_id is None and hash is None:
            raise RuntimeError
        srch = {}
        if user_id is not None:
            srch["_id"] = user_id
        if hash is not None:
            srch["hash"] = hash

        return client.images.find(srch)

    def find_images_neer(self, user_id, coords=[0, 0], distance=0):
        if len(coords) != 2:
            raise RuntimeError
        cur = client.images.find({
            "user_id": user_id,
            "geo": {"$geoWithin": {
                "$centerSphere": [coords, distance]
            }
            }
        })
        return cur


if __name__ == "__main__":
    conn = DBConnector()
    client.users.drop()
    client.images.drop()

    conn.add_user("exx", "sess")
    conn.add_user("exx", "cccc")

    bb = conn.get_user("exx")

    import pdb;

    pdb.set_trace()

