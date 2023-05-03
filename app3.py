import gradio as gr
import openai, os
from dotenv import load_dotenv

load_dotenv()
key = os.environ.get('OPENAI_API_KEY')
openai.api_key = key

messages = []
cost = 0

def add_text(history, text): 
    global messages
    history = history + [(text,'')]
    messages = messages + [{"role":'user', 'content': text}]
    #save_history(history)
    return history, ""

def generate_response(history, ):
        global messages, cost
    
        response = openai.ChatCompletion.create(
            model = "gpt-3.5-turbo",
            messages=messages,
            temperature=0.2,
        )
        print('here')
        response_msg = response.choices[0].message.content
        cost = cost + (response.usage['total_tokens'])*(0.002/1000)
        messages = messages + [{"role":'assistant', 'content': response_msg}]

        for char in response_msg:

            history[-1][1] += char
            #time.sleep(0.05)
            yield history


def add_text_for_images(history, text):
    history = history + [(text,'')]
    return history

def generate_image(history, text):
    #img_url = "https://oaidalleapiprodscus.blob.core.windows.net/private/org-T6WvejtuZhCqGecac5Yz862J/user-8LOO4C5fnrZYzYKwpILUEVUF/img-W3B70rebpSI4Gqqb2PJpPlsP.png?st=2023-04-24T02%3A11%3A04Z&se=2023-04-24T04%3A11%3A04Z&sp=r&sv=2021-08-06&sr=b&rscd=inline&rsct=image/png&skoid=6aaadede-4fb3-4698-a8f6-684d7786b067&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2023-04-24T03%3A04%3A50Z&ske=2023-04-25T03%3A04%3A50Z&sks=b&skv=2021-08-06&sig=yn/05MJTXiYSf5ECQmDgZKkoo5fvTu2jlDbcKzeFSbk%3D"
    img_url = '/home/sunil/Downloads/profilepic.jpg'
    history[-1][1] = (img_url,'')
    return history

def calc_cost():
    global cost
    return round(cost,3)

with gr.Blocks() as demo:
    
    radio = gr.Radio(value='gpt-3.5-turbo', choices=['gpt-3.5-turbo','gpt-4'], label='models')
    chatbot = gr.Chatbot(value=[], elem_id="chatbot").style(height=650)
    with gr.Row():
        with gr.Column(scale=0.90):
            txt = gr.Textbox(
                show_label=False,
                placeholder="Enter text and press enter, or upload an image",
            ).style(container=False) 
        with gr.Column(scale=0.10):
            cost_view = gr.Textbox(label='usage in $',value=0)

    txt.submit(add_text, [chatbot, txt], [chatbot, txt], queue=False).then(
            generate_response, inputs =[chatbot,],outputs = chatbot,).then(calc_cost, outputs=cost_view)
            

    # txt.submit(add_text_for_images, [chatbot, txt], chatbot).then(
    #             generate_image, [chatbot,txt], chatbot )
demo.queue()


if __name__ == "__main__":
    
    demo.launch()  