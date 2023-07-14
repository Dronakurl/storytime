import pytest

from storytime_ai import Story


@pytest.mark.asyncio
async def test_generate_from_file():
    async for _, delta in Story.generate_story_from_file(sleep_time=0.01):
        print(delta, end="")


# @pytest.mark.asyncio
# async def test_generate():
#     async for _ , delta in Story.generate_story(prompt="You are a knight in the kingdom of Larion. "):
#         print(delta,end="")

# asyncio.run(test_generate_from_file())
