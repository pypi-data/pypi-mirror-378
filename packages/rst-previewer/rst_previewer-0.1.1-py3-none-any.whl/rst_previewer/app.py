import gradio as gr
from docutils.core import publish_parts
import sys
import io
import os

def render_rst_to_html(rst_text: str) -> str:
    """
    Renders a reStructuredText string to an HTML fragment.
    """
    old_stderr = sys.stderr
    sys.stderr = captured_stderr = io.StringIO()

    try:
        parts = publish_parts(
            source=rst_text,
            writer_name='html5',
            settings_overrides={
                'initial_header_level': 1,
                'doctitle_xform': False,
                'stylesheet_path': '',
                'embed_stylesheet': False,
                'raw_enabled': True,
                'file_insertion_enabled': False,
            }
        )
        html_output = parts['html_body']
        errors = captured_stderr.getvalue()

        if errors:
            error_html = f'<pre style="background-color: #fee2e2; color: #991b1b; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #f87171; white-space: pre-wrap; font-family: monospace;">{errors}</pre>'
            html_output = error_html + html_output

        return f'<div class="p-4 sm:p-6 lg:p-8">{html_output}</div>'
    except Exception as e:
        return f'<pre style="background-color: #fee2e2; color: #991b1b; padding: 1rem; border-radius: 0.5rem;">Error: {e}</pre>'
    finally:
        sys.stderr = old_stderr

def create_gradio_app(file_path: str, serving_dir: str) -> gr.Blocks:
    """
    Creates and launches the Gradio interface for viewing an RST file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            rst_content = f.read()
    except FileNotFoundError:
        rst_content = f"Error: The file '{os.path.basename(file_path)}' was not found."
    except Exception as e:
        rst_content = f"An error occurred while reading the file: {e}"

    initial_html = render_rst_to_html(rst_content)

    with gr.Blocks(
        theme=gr.themes.Soft(font=[gr.themes.GoogleFont("Inter"), "sans-serif"]),
        css="""
            .gradio-container { max-width: 100% !important; }
            .prose {
                max-width: 80ch;
                margin: 0 auto;
            }
            .prose h1, .prose h2, .prose h3 {
                font-weight: 700;
            }
            .prose img {
                border-radius: 0.5rem;
                box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
            }
        """
    ) as demo:
        gr.Markdown(f"""
        <div class="p-4 sm:p-6 lg:p-8 text-center">
            <h1 class="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">reStructuredText Viewer</h1>
            <p class="mt-2 text-lg leading-8 text-gray-600">Viewing: <code class="bg-gray-200 p-1 rounded-md">{os.path.basename(file_path)}</code></p>
        </div>
        """)
        with gr.Row():
            with gr.Column(scale=1):
                html_output = gr.HTML(initial_html, elem_classes="prose")
    
    # Serve the directory containing the RST file to allow access to local images
    demo.allowed_paths = [serving_dir]

    return demo