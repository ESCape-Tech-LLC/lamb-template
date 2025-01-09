import uvicorn

if __name__ == "__main__":
    uvicorn.run("{{ project_name }}.asgi:application", reload=True)
