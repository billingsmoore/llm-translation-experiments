import claudette

model_name = claudette.models[1]

claud_sonet = claudette.Chat(model_name)


def claud_sonet_chat(prompt, chat_mode=True):
    global claud_sonet
    if not chat_mode:
        claud_sonet = claudette.Chat(model_name)
    response = claud_sonet(prompt)
    return "".join([textblock.text for textblock in response.content])
