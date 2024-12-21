import claudette

model_name = claudette.models[1]

claud_sonet = claudette.Chat(model_name)


def claud_sonet_chat(prompt):
    response = claud_sonet(prompt)
    return "".join([textblock.text for textblock in response.content])
