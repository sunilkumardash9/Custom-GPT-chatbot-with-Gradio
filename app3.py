import gradio as gr
import openai
import os 
import json
import time
from dotenv import load_dotenv


load_dotenv()
key = os.environ.get('KEY')
openai.api_key = key

messages  = []
cost = 0
images = []

def save_history(history):
    with open("saved_history.json", "w") as f:
        json.dump(history, f)

def load_history():
    try:
        with open("saved_history.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    
def add_text(history, text): 
    global messages
    history = history + [(text,'')]
    messages = messages + [{"role":'user', 'content': text}]
    save_history(history)
    return history, ""

def add_file(history, file):
    history = history + [((file.name,), None)]
    return history

def add_text_for_images(history, text):
    history = history + [(text,'')]

    return history


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

        save_history(history)
        
    

def generate_image(history, text):

    response = openai.Image.create(
        prompt = text,
        n=1,
        size = "256x256"

    )
    img_url = response['data'][0]['url']
    history[-1][1] = (img_url,'')
    print(history)
    return history
   
    # except:
    #     return [("Error",'')]
    

def bot(history):
    response = "**That's cool!**"
    history[-1][1] = response
    return history
    

def calc_cost():
    global cost

    return round(cost,3)

history_ = load_history()
print('yes')


with gr.Blocks() as demo:
    
    with gr.Tab(label='ChatGPT'):
        # with gr.Column(scale=0.05):
        #radio = gr.Radio(['gpt-3.5-turbo', 'gpt-4'], value = 'gpt-3.5-turbo', label = 'Choose Model', interactive=True).style(container=True)

        chatbot = gr.Chatbot(value=history_, elem_id="chatbot").style(height=650)
        
        with gr.Row():   
            with gr.Column(scale=0.85):
                txt = gr.Textbox(
                    show_label=False,
                    placeholder="Enter text and press enter, or upload an image",
                ).style(container=False)
            with gr.Column(scale=0.10, min_width=0):
                #btn = gr.UploadButton("📁", file_types=["image", "video", "audio"])
               # btn = gr.Button('click', )
                cost_view = gr.Textbox(label='usage in $',value=cost)
        
        txt.submit(add_text, [chatbot, txt], [chatbot, txt], queue=False).then(
            generate_response, inputs =[chatbot,],outputs = chatbot,).then(calc_cost, outputs=cost_view)
        
    with gr.Tab(label='Dalle-2'):
            chatbot = gr.Chatbot(value=[], elem_id="Dalle-2").style(height=750)
            with gr.Row():
                with gr.Column(scale=0.70):
                    txt = gr.Textbox(
                        show_label=False,
                        placeholder="Enter text and press enter, or upload an image",
                    ).style(container=False)
                with gr.Column(scale=0.15, min_width=0):
                    btn = gr.UploadButton("📁", file_types=["image", "video", "audio"])
                with gr.Column(scale=0.15):
                    cost_view = gr.Textbox(label='usage in $',value=cost)
        
            txt.submit(add_text_for_images, [chatbot, txt], chatbot).then(
                generate_image, [chatbot,txt], chatbot ).then(calc_cost, outputs=cost_view)
            
            btn.upload(add_file, [chatbot, btn], [chatbot]).then(
        bot, chatbot, chatbot)
  

demo.queue()
if __name__ == "__main__":
    demo.launch()  
