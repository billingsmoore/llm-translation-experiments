import claudette

model_name = claudette.models[1]


def claud_sonet_chat(prompt):
    claud_sonet = claudette.Chat(model_name)
    response = claud_sonet(prompt)
    return "".join([textblock.text for textblock in response.content])
