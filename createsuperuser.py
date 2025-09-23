import asyncio


from typer import Option, Typer
from sqlalchemy.exc import IntegrityError

from src.user.entity import UserEntity
from src.user.models.user import UserModel
from src.user.dto import UserDTO
from src.user.hash import hash_password

from src.config.database.engine import db_helper

from src.libs.exceptions import AlreadyExistError

app = Typer()

async def create_user(user_entity: UserEntity):
    # Get the session from the async generator
    async for session in db_helper.get_session():  # Use async for to get the session
        user = UserModel(**user_entity.__dict__)
        session.add(user)
        try:
            await session.commit()
            print(f"{user.name} {user.login} successfully created")
        except IntegrityError:
            await session.rollback()
            raise AlreadyExistError(f"{user.login} already exists")
        finally:
            await session.close()
        break  # Exit after one iteration (we only need one session)

@app.command()
def hello(name: str):
    print(f"Hello {name}")

@app.command(help="Create a new admin user")
def createsuperuser(
    name: str = Option(default="admin", help="user name", prompt=True),
    surname: str = Option(default="admin", help="user surname", prompt=True),
    login: str = Option("admin", help="user login", prompt=True),
    password: str = Option("admin", prompt="user password", hide_input=True),
    is_admin: bool = Option(False, help="is user admin", prompt=True),
):
    dto = UserDTO(
        name=name,
        surname=surname,
        login=login,
        password=hash_password(password),
        is_admin=bool(is_admin)
    )
    user_entity = UserEntity(**dto.model_dump(exclude_none=True))

    # Run the async function from a sync context
    asyncio.run(create_user(user_entity))

if __name__ == "__main__":
    app()