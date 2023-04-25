import os
import requests
import werkzeug
import gradio as gr
from urllib.parse import urlparse
from modules import script_callbacks

root = "/content"
sd_path = "/stable-diffusion-webui"

def folder(content_type):
    if content_type == "Checkpoint":
       return gr.Textbox.update(value="/models/Stable-diffusion")
    elif content_type == "Hypernetwork":
         return gr.Textbox.update(value="/models/hypernetworks")
    elif content_type == "TextualInversion/Embedding":
         return gr.Textbox.update(value="/embeddings")
    elif content_type == "AestheticGradient":
         return gr.Textbox.update(value="/extensions/stable-diffusion-webui-aesthetic-gradients/aesthetic_embeddings")
    elif content_type == "VAE":
         return gr.Textbox.update(value="/models/VAE")
    elif content_type == "LoRA":
         return gr.Textbox.update(value="/models/Lora")
    elif content_type == "LyCORIS(LoCon/LoHA)":
         return gr.Textbox.update(value="/models/LyCORIS")

def get_filename_from_url(url=None):
    if url is None:
       return None        
    with requests.get(url, stream=True) as req:
        if content_disposition := req.headers.get("Content-Disposition"):
            param, options = werkzeug.http.parse_options_header(content_disposition)
            if param == 'attachment' and (filename := options.get('filename')):
                f = filename.replace(" ", "_")
                return f
        path = urlparse(req.url).path
        n = path[path.rfind('/') + 1:]
        name = n.replace(" ", "_")
        return name

def change_filename(filename1, filename):
    if filename1 == "Use original Filename from the Source":
       return gr.Textbox(filename).update(visible=False)
    elif filename1 == "Create New Filename(Recomended)":
         return gr.Textbox(filename).update(visible=True)

def combine(url, content_type1, filename):
    return gr.Textbox.update(value=f"aria2c --console-log-level=error -c -x 16 -s 16 -k 1M {url} -d {root}{sd_path}{content_type1} -o {filename}")

def info_update(url, content_type1, filename, info):
    return gr.Textbox.update(value=f"[URL]:  {url}\n[Folder Path]:  {content_type1}\n[File Name]:  {filename}")
    
def run(command):
    with os.popen(command) as pipe:
         for line in pipe:
             line = line.rstrip()
             print(line)
             yield line    

def on_ui_tabs():
    with gr.Blocks() as downloader:    
         with gr.Row():
              with gr.Column(scale=2):
                   content_type = gr.Radio(label="1. Choose Content type", choices=["Checkpoint","Hypernetwork","TextualInversion/Embedding","AestheticGradient", "VAE", "LoRA", "LyCORIS(LoCon/LoHA)"])
                   content_type1 = gr.Textbox(visible=False)
                   content_type.change(fn=folder, inputs=content_type, outputs=content_type1)
         with gr.Row():
              url = gr.Textbox(label="2. Put Link Download Below", max_lines=1, placeholder="Type/Paste URL Here")
         with gr.Row():
              with gr.Column(scale=2):
                   filename1 = gr.Radio(label="Setting Filename", choices=["Use original Filename from the Source", "Create New Filename(Recomended)"], type="value", value="Use original Filename from the Source")
         with gr.Row():
              filename = gr.Textbox(label="3. Create new Filename", placeholder="Type/Paste Filename.extension Here", visible=False, interactive=True)
              filename1.change(fn=change_filename, inputs=[filename1, filename], outputs=filename)
         with gr.Row():
              commands = gr.Textbox(value=f"aria2c --console-log-level=error -c -x 16 -s 16 -k 1M", label="Information Command", visible=False, interactive=False)
              info = gr.Textbox(value="[URL]:\n[Folder Path]:\n[File Name]:", label="Information", placeholder="Make sure to Check properly whether everything is Correct", lines=3, interactive=False)
         with gr.Row():
              content_type1.change(fn=combine, inputs=[url, content_type1, filename], outputs=commands)
              url.change(fn=combine, inputs=[url, content_type1, filename], outputs=commands)
              url.change(fn=get_filename_from_url, inputs=url, outputs=filename)
              filename.change(fn=combine, inputs=[url, content_type1, filename], outputs=commands)
              content_type1.change(fn=info_update, inputs=[url, content_type1, filename], outputs=info)
              url.change(fn=info_update, inputs=[url, content_type1, filename], outputs=info)
              filename.change(fn=info_update, inputs=[url, content_type1, filename], outputs=info)
         with gr.Row():
              download_btn = gr.Button("Start Download")
              out_text = gr.Textbox(label="Download Result", placeholder="Result", show_progress=True)
              download_btn.click(fn=run, inputs=commands, outputs=out_text)
              url.submit(fn=run, inputs=commands, outputs=out_text)
              filename.submit(fn=run, inputs=commands, outputs=out_text)

    downloader.queue(concurrency_count=5)
    return (downloader, "Model Downloader", "downloader"),
    
script_callbacks.on_ui_tabs(on_ui_tabs)
