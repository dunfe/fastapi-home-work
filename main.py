from typing import Annotated, List

from sqlalchemy.orm import Session

from crud import (create_company, create_task, create_user, get_companies,
                  get_company, get_task, get_tasks, get_user,
                  get_user_by_username, get_users)
from database import SessionLocal, engine
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from models import Base
from schemas import Company, CompanyCreate, Task, TaskCreate, User, UserCreate

app = FastAPI()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


Base.metadata.create_all(bind=engine)


async def check_admin(
    token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)
):
    user = get_user_by_username(db, username=token)
    if user.is_admin == False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )
    return user


@app.post("/tasks/", response_model=Task)
def add_task(task: TaskCreate, db: Session = Depends(get_db)):
    return create_task(db=db, task=task)


@app.get("/tasks/", response_model=List[Task])
def read_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    tasks = get_tasks(db, skip=skip, limit=limit)
    return tasks


@app.get("/tasks/{task_id}", response_model=Task)
def read_task(task_id: int, db: Session = Depends(get_db)):
    db_task = get_task(db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task


@app.post("/users/", response_model=User)
def add_user(
    user: UserCreate, db: Session = Depends(get_db), token: str = Depends(check_admin)
):
    return create_user(db=db, user=user)


@app.get("/users/", response_model=List[User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=User)
def read_user(
    user_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    db_user = get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/companies/", response_model=Company)
def add_company(
    company: CompanyCreate,
    db: Session = Depends(get_db),
    token: str = Depends(check_admin),
):
    return create_company(db=db, company=company)


@app.get("/companies/", response_model=List[Company])
def read_companies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    companies = get_companies(db, skip=skip, limit=limit)
    return companies


@app.get("/companies/{company_id}", response_model=Company)
def read_company(company_id: int, db: Session = Depends(get_db)):
    db_company = get_company(db, company_id=company_id)
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return db_company


@app.post("/login")
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
    user_dict: User = get_user_by_username(db, username=form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect credentials")

    if user_dict.password != form_data.password:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    # return fake access token
    return {"access_token": user_dict.username, "token_type": "bearer"}
