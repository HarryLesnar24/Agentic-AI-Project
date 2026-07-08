


def get_langfuse_config(session_id: str) -> dict:
    config = {
        "configurable": {
            "thread_id": session_id
        }
    }

    return config

