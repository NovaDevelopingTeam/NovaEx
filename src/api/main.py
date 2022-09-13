from fastapi import FastAPI
from db import make_db
import pickle
import sqlite3

app = FastAPI()
make_db()

db = sqlite3.connect("novaex.db")
c = db.cursor()

@app.get("/points/{user_id}")
async def get_points(user_id: int) -> int:
    """
        :param user_id: The ID of the user to get points for.
        :return: int: The number of current points (not counting points in websites)
    """
    return c.execute("SELECT points FROM users WHERE id=?", (user_id,)).fetchone()[0]

@app.post("/add/{user_id}/{points}")
async def add_point(user_id: int, points: int) -> bool:
    """
        :param user_id: The ID of the user to add points for.
        :param points: The number of points to add to the user.
        :return: bool: True if succesfully added, False if database error occurs or user not found.
    """
    # TODO: authentication for "system user"
    r = c.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()[0]
    if r == None:
        return False
    try:
        cur_points = c.execute("SELECT points FROM users WHERE id=?", (user_id,)).fetchone()[0]
        c.execute("UPDATE users SET points=?", (cur_points + points,))
        db.commit()
        return True
    except:
        return False
        
@app.post("/add-website/{user_id}/{url}")
async def add_website(user_id: int, url: str):
    """
        :param user_id: The user to add the website to.
        :return: bool: True if succesfully added, False if database error occurs or user not found.
    """
    # TODO: authentication for TBD in project planning
    r = c.execute("SELECT sites FROM users where id = ?", (user_id,)).fetchone()[0]
    if r == None:
        return False
    try:
        if r == "no websites":
            sites = pickle.dumps([url])
            c.execute("UPDATE users SET sites = ? WHERE id=?", (sites, user_id))
            db.commit()
            return True
        else:
            sites_list = pickle.loads(r)
            sites_list.append(url)
            sites = pickle.dumps(sites_list)
            c.execute("UPDATE users SET sites = ? WHERE id=?", (sites, user_id))
            db.commit()
            return True
    except:
        return False

    