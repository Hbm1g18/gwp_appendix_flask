from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import pandas as pd
import os
import subprocess
import shutil
from PIL import Image
import zipfile
import concurrent.futures

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join('static', 'uploads')
GENERATION_FOLDER = os.path.join('static', 'generation')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
root = os.getcwd()

@app.route('/', methods=['GET', 'POST'])
def index():
    os.chdir(root)
    generation_folder = os.path.join('static', 'generation')
    if os.path.exists(generation_folder):
        for item in os.listdir(generation_folder):
            item_path = os.path.join(generation_folder, item)
            if os.path.isfile(item_path):
                os.remove(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)

    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file part"
        
        file = request.files['file']
        
        if file.filename == '':
            return "No selected file"
        
        if not file.filename.endswith('.csv'):
            return "Please upload a CSV file"
        
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        
        try:
            df = pd.read_csv(file_path, sep='\t')
            headers = df.columns.tolist()
            
            return render_template('upload.html', headers=headers, df=df, filename=file.filename)
        except Exception as e:
            return f"Error reading CSV file: {str(e)}"

    return render_template('index.html')

@app.route('/process_data', methods=['POST'])
def process_data():
    if request.method == 'POST':
        filename = request.form.get('filename')

        project = request.form.get('project')
        client = request.form.get('client')
        appendix = request.form.get('appendix')
        notes = request.form.get('notes') 

        split_data = request.form.get('split_data')
        split_field = request.form.get('split_field_dropdown') if split_data == 'true' else None

        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        df = pd.read_csv(file_path, sep='\t')

        selected_headers = [request.form.get(f'header{i}') for i in range(0, int(request.form.get('header_count')) + 1)]
        selected_headers.append("URLs")
        selected_headers.append("ObjectID")

        df_urls = df.assign(URLs=df['URLs'].str.split(',')).explode('URLs')

        df_urls.reset_index(drop=True, inplace=True)
        df_urls.reset_index(inplace=True)
        df_urls.rename(columns={'index': 'Index'}, inplace=True)
        df_urls['Index'] += 1
        df_urls.to_csv("checkme.csv")

        generation_photos_folder = os.path.join(GENERATION_FOLDER, 'photos')
        if not os.path.exists(generation_photos_folder):
            os.makedirs(generation_photos_folder)

        os.chdir(GENERATION_FOLDER)

        with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
            futures = []

            for index, row in df_urls.iterrows():
                url = row['URLs']
                future = executor.submit(download_image, url, index)
                futures.append(future)

            for future in concurrent.futures.as_completed(futures):
                index, error = future.result()
                if error:
                    print(f"Error downloading image {index}: {error}")

        image_files = [f'photos/{index}.png' for index in range(1, len(df_urls) + 1)]
        images_df = pd.DataFrame({'Index': range(1, len(df_urls) + 1), 'File_Path': image_files})


                # -------------------------------------------------------------------------------------------------------------------------------
        # Define your base TeX template
        base_template = r"""
        \documentclass[12pt, letterpaper]{article}
        \usepackage{graphicx}
        \usepackage{subcaption}
        \usepackage[left=10mm,right=10mm,top=5mm,bottom=5mm,paper=a4paper]{geometry}
        \usepackage{multirow}
        \usepackage{caption}  % Added for \captionof
        \usepackage{xcolor}
        \usepackage{fontspec}
        \setmainfont{Tahoma}
        \usepackage[utf8]{inputenc}
        \batchmode

        \setlength{\fboxsep}{0pt} % <-- Add this line
        \captionsetup[subfigure]{labelformat=empty}

        \begin{document}
        """

        # Define the section template to be added
        a4section_template = r"""
        \begin{figure}[h]
            \centering
            \fbox{\parbox{1\linewidth}{
            \vspace{5mm}
                    \begin{subfigure}{\linewidth}
                        \centering
                        \includegraphics[height=#img_width#\textheight, angle=#angle#]{#photopath1#}
                        \captionsetup{width=0.8\linewidth}
                        \caption{#comment_string#}
                    \end{subfigure}

                    \vspace{1mm}
                    \hrule
                \begin{minipage}[c][4.5cm][t]{1\textwidth} 
                    \begin{minipage}[t][2cm][t]{0.5\textwidth} 
	 				\vspace{2mm}
					\centering
					\textbf{\small{NOTES:}} \\ 
					\raggedright 
					\begin{itemize}
            					\item \footnotesize{#notes#}
       				 	\end{itemize}
                            	\end{minipage}
				\vrule
				\begin{minipage}[t][2cm][t]{0.5\textwidth} 
                                		\vspace{2mm}     
                                		\hspace{2mm}
                                    	\raggedright
                                		\text{\small{\textcolor[rgb]{0.1255,0.3058,0.4745}{Client:}} \\ 
                                		\hspace{6mm} \footnotesize{#client#}} 
                                \end{minipage}
                                \hrule
                                \begin{minipage}[c][2.5cm][c]{0.5\textwidth} 
        					\centering
                				\includegraphics[height=2.3cm]{../logo/gwp.png}
            			\end{minipage}
				\vrule
				\begin{minipage}[c][2.5cm][c]{0.495\textwidth} 
        				\begin{minipage}[c][1.3cm][c]{1\textwidth} 
            				\vspace{2mm}
            				\hspace*{2mm}
            				\raggedright
            				\text{\small{\textcolor[rgb]{0.1255,0.3058,0.4745}{Project: }} \\ 
                				\hspace{6mm} \footnotesize{#project#}}
        				\end{minipage}
        				\hrule
        				\begin{minipage}[c][1.2cm][t]{1\textwidth} 
            				\begin{minipage}[c][1.2cm][t]{0.7\textwidth}    
        						\vspace{1mm}
       						\hspace{2mm}
            					\raggedright
        						\text{\small{\textcolor[rgb]{0.1255,0.3058,0.4745}{Drawing No}} \\ 
        						\hspace{6mm} \footnotesize{#appendix#}} 
        					\end{minipage}
        					\vline
        					\begin{minipage}[c][1.2cm][t]{0.2\textwidth}   
        						\vspace{1mm}
        						\hspace{2mm}
            					\raggedright
        						\text{\small{\textcolor[rgb]{0.1255,0.3058,0.4745}{Version}} \\ 
        						\hspace{12mm} \footnotesize{a}} 
        					\end{minipage}	
        				\end{minipage}
    				\end{minipage}
                    \end{minipage} 
                }}
        \end{figure}
        \clearpage
        """

        # ---------------------------------------------------------End A4 Template-----------------------------------------------------

        # ---------------------------------------------------------Start 2 page Template-----------------------------------------------------
        # Update the section template to include two subfigures per page
        two_pagesection_template = r"""
        \begin{figure}[h]
            \centering
            \fbox{\parbox{1\linewidth}{
            \vspace{5mm}
                \begin{subfigure}{\linewidth}
                    \centering
                    \includegraphics[width=0.37\textheight, angle=#angle1#]{#photopath1#}
                    \captionsetup{width=0.8\linewidth}
                    \caption{#CAPTION1#}
                \end{subfigure}

                \vspace{\baselineskip}

                \begin{subfigure}{\linewidth}
                    \centering
                    \includegraphics[width=0.37\textheight, angle=#angle2#]{#photopath2#}
                    \captionsetup{width=0.8\linewidth}
                    \caption{#CAPTION2#}
                \end{subfigure}
                    \vspace{1mm}
                    \hrule
                \begin{minipage}[c][4.5cm][t]{1\textwidth} 
                    \begin{minipage}[t][2cm][t]{0.5\textwidth} 
	 				\vspace{2mm}
					\centering
					\textbf{\small{NOTES:}} \\ 
					\raggedright 
					\begin{itemize}
            					\item \footnotesize{#notes#}
       				 	\end{itemize}
                            	\end{minipage}
				\vrule
				\begin{minipage}[t][2cm][t]{0.5\textwidth} 
                                		\vspace{2mm}     
                                		\hspace{2mm}
                                    	\raggedright
                                		\text{\small{\textcolor[rgb]{0.1255,0.3058,0.4745}{Client:}} \\ 
                                		\hspace{6mm} \footnotesize{#client#}} 
                                \end{minipage}
                                \hrule
                                \begin{minipage}[c][2.5cm][c]{0.5\textwidth} 
        					\centering
                				\includegraphics[height=2.3cm]{../logo/gwp.png}
            			\end{minipage}
				\vrule
				\begin{minipage}[c][2.5cm][c]{0.495\textwidth} 
        				\begin{minipage}[c][1.3cm][c]{1\textwidth} 
            				\vspace{2mm}
            				\hspace*{2mm}
            				\raggedright
            				\text{\small{\textcolor[rgb]{0.1255,0.3058,0.4745}{Project: }} \\ 
                				\hspace{6mm} \footnotesize{#project#}}
        				\end{minipage}
        				\hrule
        				\begin{minipage}[c][1.2cm][t]{1\textwidth} 
            				\begin{minipage}[c][1.2cm][t]{0.7\textwidth}    
        						\vspace{1mm}
       						\hspace{2mm}
            					\raggedright
        						\text{\small{\textcolor[rgb]{0.1255,0.3058,0.4745}{Drawing No}} \\ 
        						\hspace{6mm} \footnotesize{#appendix#}} 
        					\end{minipage}
        					\vline
        					\begin{minipage}[c][1.2cm][t]{0.2\textwidth}   
        						\vspace{1mm}
        						\hspace{2mm}
            					\raggedright
        						\text{\small{\textcolor[rgb]{0.1255,0.3058,0.4745}{Version}} \\ 
        						\hspace{12mm} \footnotesize{a}} 
        					\end{minipage}	
        				\end{minipage}
    				\end{minipage}
                    \end{minipage} 
                }}
        \end{figure}
        \clearpage
        """

# END TEMPLATES///////////////////////////////////////////////////////////////////////////////////////////////////////
        split_field = request.form.get('split_field_dropdown') if split_data == 'true' else None


        if split_data == 'true':
            split_areas=[]
            split_areas.extend(df_urls[split_field].unique())

            for area in split_areas:
                df_split = df_urls[df_urls[split_field] == area]

                tex_content = base_template
                if 'two_per_page' in request.form and request.form['two_per_page'] == 'true':
                    for i in range(0, len(df_split), 2):
                        # Fetch data for the first entry
                        row1 = df_split.iloc[i]
                        photo1 = row1['Index']
                        object_id1 = row1['ObjectID']
                        chosen_headers1 = ", ".join([str(row1[header]) for header in selected_headers if header != 'ObjectID' and header != 'URLs'])
                        comment_string1 = f"Photograph {object_id1} - {chosen_headers1}"
                        file_path1 = images_df.loc[images_df['Index'] == row1['Index'], 'File_Path'].values[0]

                        if i+1 < len(df_split):
                            row2 = df_split.iloc[i+1]
                            photo2 = row2['Index']
                            object_id2 = row2['ObjectID']
                            chosen_headers2 = ", ".join([str(row2[header]) for header in selected_headers if header != 'ObjectID' and header != 'URLs'])
                            comment_string2 = f"Photograph {object_id2} - {chosen_headers2}"
                            file_path2 = images_df.loc[images_df['Index'] == row2['Index'], 'File_Path'].values[0]
                        else:
                            row2 = row1
                            photo2 = row2['Index']
                            object_id2 = row2['ObjectID']
                            chosen_headers2 = ", ".join([str(row2[header]) for header in selected_headers if header != 'ObjectID' and header != 'URLs'])
                            comment_string2 = f"Photograph {object_id2} - {chosen_headers2}"
                            file_path2 = images_df.loc[images_df['Index'] == row2['Index'], 'File_Path'].values[0]

                        with Image.open(file_path1) as img1:
                            width1, height1 = img1.size
                            if hasattr(img1, '_getexif'):
                                exif1 = img1._getexif()
                                if exif1:
                                    orientation1 = exif1.get(274)
                                    if orientation1 in [5, 6, 7, 8]:
                                        width1, height1 = height1, width1
                                        angle1 = -90
                                    else:
                                        angle1 = 0
                            else:
                                angle1 = 0

                        with Image.open(file_path2) as img2:
                            width2, height2 = img2.size
                            if hasattr(img2, '_getexif'):
                                exif2 = img2._getexif()
                                if exif2:
                                    orientation2 = exif2.get(274)
                                    if orientation2 in [5, 6, 7, 8]:
                                        width2, height2 = height2, width2
                                        angle2 = -90
                                    else:
                                        angle2 = 0
                            else:
                                angle2 = 0

                        section_content = two_pagesection_template.replace("#photopath1#", file_path1)\
                            .replace("#photopath2#", file_path2)\
                            .replace("#CAPTION1#", comment_string1)\
                            .replace("#CAPTION2#", comment_string2)\
                            .replace("#angle1#", str(angle1))\
                            .replace("#angle2#", str(angle2))\
                            .replace("#project#", project)\
                            .replace("#client#", client)\
                            .replace("#notes#", notes)\
                            .replace("#appendix#", appendix)

                        tex_content += section_content

                else:
                    for index, row in df_split.iterrows():
                        if index < len(images_df):
                            photo = row['Index']
                            object_id = row['ObjectID']
                            chosen_headers = ", ".join([str(row[header]) for header in selected_headers if header != 'ObjectID' and header != 'URLs'])
                            comment_string = ""
                            comment_string += f"Photograph {object_id} - {chosen_headers}"

                            file_path = images_df.loc[index, 'File_Path']
                            with Image.open(file_path) as img:
                                
                                width, height = img.size
                                
                                if hasattr(img, '_getexif'):
                                    exif = img._getexif()
                                    if exif:
                                        orientation = exif.get(274)
                                        if orientation in [5, 6, 7, 8]:
                                            width, height = height, width
                                            angle = -90
                                            img_width = 0.37
                                        else:
                                            angle = 0
                                            img_width = 0.42
                                else:
                                    angle = 0
                                    img_width = 0.42
                            section_content = a4section_template.replace("#photopath1#", file_path)\
                                                                .replace("#comment_string#", comment_string)\
                                                                .replace("#angle#", str(angle))\
                                                                .replace("#img_width#", str(img_width))\
                                                                .replace("#project#", project)\
                                                                .replace("#client#", client)\
                                                                .replace("#notes#", notes)\
                                                                .replace("#appendix#", appendix)
                            tex_content += section_content
                # ---------------------------------------------------------End 2 page Template-----------------------------------------------------

                tex_content += r"\end{document}"

                with open(f"{area}.tex", "w") as tex_file:
                    tex_file.write(tex_content)
                
                subprocess.run(["lualatex", f"{area}.tex"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            with zipfile.ZipFile("output.zip", "w") as zip_file:
                for area in split_areas:
                    pdf_file = f"{area}.pdf"
                    if os.path.exists(pdf_file):
                        zip_file.write(pdf_file)
            return render_template('download.html', filename="output.zip")

        else:
            tex_content = base_template
            if 'two_per_page' in request.form and request.form['two_per_page'] == 'true':
                for i in range(0, len(df_urls), 2):
                    row1 = df_urls.iloc[i]
                    photo1 = row1['Index']
                    object_id1 = row1['ObjectID']
                    chosen_headers1 = ", ".join([str(row1[header]) for header in selected_headers if header != 'ObjectID' and header != 'URLs'])
                    comment_string1 = f"Photograph {object_id1} - {chosen_headers1}"
                    file_path1 = images_df.loc[i, 'File_Path']

                    if i+1 < len(df_urls):
                        row2 = df_urls.iloc[i+1]
                        photo2 = row2['Index']
                        object_id2 = row2['ObjectID']
                        chosen_headers2 = ", ".join([str(row2[header]) for header in selected_headers if header != 'ObjectID' and header != 'URLs'])
                        comment_string2 = f"Photograph {object_id2} - {chosen_headers2}"
                        file_path2 = images_df.loc[i+1, 'File_Path']
                    else:
                        row2 = row1
                        photo2 = row2['Index']
                        object_id2 = row2['ObjectID']
                        chosen_headers2 = ", ".join([str(row2[header]) for header in selected_headers if header != 'ObjectID' and header != 'URLs'])
                        comment_string2 = f"Photograph {object_id2} - {chosen_headers2}"
                        file_path2 = images_df.loc[i, 'File_Path']

                    with Image.open(file_path1) as img1:
                        width1, height1 = img1.size
                        if hasattr(img1, '_getexif'):
                            exif1 = img1._getexif()
                            if exif1:
                                orientation1 = exif1.get(274)
                                if orientation1 in [5, 6, 7, 8]:
                                    width1, height1 = height1, width1
                                    angle1 = -90
                                else:
                                    angle1 = 0
                        else:
                            angle1 = 0

                    with Image.open(file_path2) as img2:
                        width2, height2 = img2.size
                        if hasattr(img2, '_getexif'):
                            exif2 = img2._getexif()
                            if exif2:
                                orientation2 = exif2.get(274)
                                if orientation2 in [5, 6, 7, 8]:
                                    width2, height2 = height2, width2
                                    angle2 = -90
                                else:
                                    angle2 = 0
                        else:
                            angle2 = 0

                    section_content = two_pagesection_template.replace("#photopath1#", file_path1)\
                        .replace("#photopath2#", file_path2)\
                        .replace("#CAPTION1#", comment_string1)\
                        .replace("#CAPTION2#", comment_string2)\
                        .replace("#angle1#", str(angle1))\
                        .replace("#angle2#", str(angle2))\
                        .replace("#project#", project)\
                        .replace("#client#", client)\
                        .replace("#notes#", notes)\
                        .replace("#appendix#", appendix)
                    tex_content += section_content

            else:
                for index, row in df_urls.iterrows():
                    if index < len(images_df):
                        photo = row['Index']
                        object_id = row['ObjectID']
                        chosen_headers = ", ".join([str(row[header]) for header in selected_headers if header != 'ObjectID' and header != 'URLs'])
                        comment_string = ""
                        comment_string += f"Photograph {object_id} - {chosen_headers}"

                        file_path = images_df.loc[index, 'File_Path']
                        with Image.open(file_path) as img:
                            
                            width, height = img.size
                            if hasattr(img, '_getexif'):
                                exif = img._getexif()
                                if exif:
                                    orientation = exif.get(274)
                                    if orientation in [5, 6, 7, 8]:
                                        width, height = height, width
                                        angle = -90
                                        img_width = 0.37
                                    else:
                                        angle = 0
                                        img_width = 0.42
                            else:
                                angle = 0
                                img_width = 0.42
                        section_content = a4section_template.replace("#photopath1#", file_path)\
                                                            .replace("#comment_string#", comment_string)\
                                                            .replace("#angle#", str(angle))\
                                                            .replace("#img_width#", str(img_width))\
                                                            .replace("#project#", project)\
                                                            .replace("#client#", client)\
                                                            .replace("#notes#", notes)\
                                                            .replace("#appendix#", appendix)
                        tex_content += section_content
            tex_content += r"\end{document}"
            with open("output.tex", "w") as tex_file:
                tex_file.write(tex_content)
            subprocess.run(["lualatex", f"output.tex"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return render_template('download.html', filename="output.pdf")
    
@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(GENERATION_FOLDER, filename, as_attachment=True)

def download_image(url, index):
    try:
        subprocess.run(['curl', '-o', f'photos/{index+1}.png', url], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return index, None 
    except Exception as e:
        return None, e  

# local
# if __name__ == '__main__':
#      app.run(host="0.0.0.0", port=5050, debug=True, ssl_context=('cert.pem', 'key.pem'))

# docker
if __name__ == '__main__':
   app.run(ssl_context=('cert.pem', 'key.pem'), host='0.0.0.0')
