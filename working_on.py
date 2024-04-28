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

                    \vspace{\baselineskip}

                    \hrule
                    \begin{minipage}[c][3.5cm][t]{0.4\textwidth} % Larger Left side
                            %\centering
                        \begin{minipage}[t][1.5cm][t]{0.4\textwidth} % Set explicit width for Right top
                        \vspace{2mm}
                        \hspace{2mm}
                            \raggedright
                            \textbf{\small{Notes:} \footnotesize{#notes#}}

                        \end{minipage}
                        \hrule
                                \begin{minipage}[c][2cm][c]{\textwidth} % Adjust height and alignment
                            \centering
                                    \includegraphics[height=1.8cm]{photos/1.png}
                                \end{minipage}
                        \end{minipage}%
                        \vline % Vertical line
                        \begin{minipage}[c][3cm][t]{0.6\textwidth} % Larger Right side with no indentation
                            \begin{minipage}[c][1cm][t]{0.8\textwidth} % Set explicit width for Right top
                        \vspace{2mm}     
                        \hspace{2mm}
                            \raggedright
                        \textbf{\small{Client: } \footnotesize{#client#}} 
                            \end{minipage}
                            \hrule % Horizontal line
                            \begin{minipage}[c][1.4cm][t]{0.9\textwidth} % Set explicit width for Right bottom
                                \vspace{2mm}
                                \hspace*{2mm}
                                \raggedright
                                \parbox[t]{\linewidth}{\textbf{\small{Project:}} {\hangindent=2mm #project#}}
                            \end{minipage}
                            \hrule % Horizontal line
                            \begin{minipage}[c][0.6cm][t]{0.8\textwidth} % Set explicit width for Right bottom    
                        \vspace{2mm}
                        \hspace{2mm}
                            \raggedright
                        \textbf{\footnotesize Appendix: #appendix#} 
                            \end{minipage}
                        \end{minipage}
                    
                }}
        \end{figure}
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
                    %\label{fig:dragon1}
                \end{subfigure}

                \vspace{\baselineskip}

                \begin{subfigure}{\linewidth}
                    \centering
                    \includegraphics[width=0.37\textheight, angle=#angle2#]{#photopath2#}
                    \captionsetup{width=0.8\linewidth}
                    \caption{#CAPTION2#}
                    %\label{fig:dragon1}
                \end{subfigure}

                    \vspace{\baselineskip}

                    \hrule
                    \begin{minipage}[c][3.5cm][t]{0.4\textwidth} % Larger Left side
                            \begin{minipage}[t][1.5cm][t]{0.4\textwidth} % Set explicit width for Right top
                            \vspace{2mm}
                            \hspace{2mm}
                                \raggedright
                                \textbf{\small{Notes:} \footnotesize{#notes#}}

                            \end{minipage}
                            \hrule
                                    \begin{minipage}[c][2cm][c]{\textwidth} % Adjust height and alignment
                                \centering
                                        \includegraphics[height=1.8cm]{photos/1.png}
                                    \end{minipage}
                            \end{minipage}%
                            \vline % Vertical line
                            \begin{minipage}[c][3cm][t]{0.6\textwidth} % Larger Right side with no indentation
                                \begin{minipage}[c][1cm][t]{0.8\textwidth} % Set explicit width for Right top
                                \vspace{2mm}     
                                \hspace{2mm}
                                    \raggedright
                                \textbf{\small{Client: } \footnotesize{#client#}} 
                                \end{minipage}
                                \hrule % Horizontal line
                                \begin{minipage}[c][1.4cm][t]{0.9\textwidth} % Set explicit width for Right bottom
                                    \vspace{2mm}
                                    \hspace*{2mm}
                                    \raggedright
                                    \parbox[t]{\linewidth}{\textbf{\small{Project:}} {\hangindent=2mm #project#}}
                                \end{minipage}
                                \hrule % Horizontal line
                                \begin{minipage}[c][0.6cm][t]{0.8\textwidth} % Set explicit width for Right bottom    
                                \vspace{2mm}
                                \hspace{2mm}
                                    \raggedright
                                \textbf{\footnotesize Appendix: #appendix#} 
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
                df_split = df[df_urls[split_field] == area]

                tex_content = base_template
                # Update the iteration process to iterate over two rows at a time
                if 'two_per_page' in request.form and request.form['two_per_page'] == 'true':
                    for i in range(0, len(df_split), 2):
                        # Fetch data for the first entry
                        row1 = df_split.iloc[i]
                        photo1 = row1['Index']
                        object_id1 = row1['ObjectID']
                        chosen_headers1 = ", ".join([str(row1[header]) for header in selected_headers if header != 'ObjectID' and header != 'URLs'])
                        comment_string1 = f"Photograph {object_id1} - {chosen_headers1}"
                        file_path1 = images_df.loc[i, 'File_Path']

                        # Fetch data for the second entry
                        if i+1 < len(df_split):
                            row2 = df_split.iloc[i+1]
                            photo2 = row2['Index']
                            object_id2 = row2['ObjectID']
                            chosen_headers2 = ", ".join([str(row2[header]) for header in selected_headers if header != 'ObjectID' and header != 'URLs'])
                            comment_string2 = f"Photograph {object_id2} - {chosen_headers2}"
                            file_path2 = images_df.loc[i+1, 'File_Path']
                        else:
                            # If the number of entries is odd, duplicate the last entry
                            row2 = row1
                            photo2 = row2['Index']
                            object_id2 = row2['ObjectID']
                            chosen_headers2 = ", ".join([str(row2[header]) for header in selected_headers if header != 'ObjectID' and header != 'URLs'])
                            comment_string2 = f"Photograph {object_id2} - {chosen_headers2}"
                            file_path2 = images_df.loc[i, 'File_Path']

                        # Open and process the first image
                        with Image.open(file_path1) as img1:
                            width1, height1 = img1.size
                            if hasattr(img1, '_getexif'):
                                exif1 = img1._getexif()
                                if exif1:
                                    orientation1 = exif1.get(274)
                                    if orientation1 in [5, 6, 7, 8]:
                                        width1, height1 = height1, width1  # Swap width and height
                                        angle1 = -90
                                    else:
                                        angle1 = 0
                            else:
                                angle1 = 0

                        # Open and process the second image
                        with Image.open(file_path2) as img2:
                            width2, height2 = img2.size
                            if hasattr(img2, '_getexif'):
                                exif2 = img2._getexif()
                                if exif2:
                                    orientation2 = exif2.get(274)
                                    if orientation2 in [5, 6, 7, 8]:
                                        width2, height2 = height2, width2  # Swap width and height
                                        angle2 = -90
                                    else:
                                        angle2 = 0
                            else:
                                angle2 = 0

                        # Build the TeX content using the two-page section template
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

                        # Append the section content to the overall TeX content
                        tex_content += section_content

                else:
                    for index, row in df_split.iterrows():
                        # Check if the index exists in images_df
                        if index < len(images_df):
                            # Fetch data from df_urls
                            photo = row['Index']
                            object_id = row['ObjectID']
                            chosen_headers = ", ".join([str(row[header]) for header in selected_headers if header != 'ObjectID' and header != 'URLs'])
                            comment_string = ""
                            comment_string += f"Photograph {object_id} - {chosen_headers}"

                            # Fetch data from images_df
                            file_path = images_df.loc[index, 'File_Path']
                            with Image.open(file_path) as img:
                                print(f"Opening {file_path}")
                                
                                width, height = img.size
                                
                                # Check if the image has orientation metadata
                                if hasattr(img, '_getexif'):
                                    exif = img._getexif()
                                    if exif:
                                        orientation = exif.get(274)
                                        if orientation in [5, 6, 7, 8]:
                                            # Swap width and height
                                            width, height = height, width
                                            angle = -90
                                            img_width = 0.37
                                        else:
                                            angle = 0
                                            img_width = 0.42
                                else:
                                    angle = 0
                                    img_width = 0.42

                            # Build the TeX content using the section template
                            section_content = a4section_template.replace("#photopath1#", file_path)\
                                                                .replace("#comment_string#", comment_string)\
                                                                .replace("#angle#", str(angle))\
                                                                .replace("#img_width#", str(img_width))\
                                                                .replace("#project#", project)\
                                                                .replace("#client#", client)\
                                                                .replace("#notes#", notes)\
                                                                .replace("#appendix#", appendix)

                            # Append the section content to the overall TeX content
                            tex_content += section_content




                # ---------------------------------------------------------End 2 page Template-----------------------------------------------------


                # Close the TeX document
                tex_content += r"\end{document}"

                # Write the generated TeX content to a file
                with open(f"{area}.tex", "w") as tex_file:
                    tex_file.write(tex_content)

        else:
    
            tex_content = base_template
            # Update the iteration process to iterate over two rows at a time
            if 'two_per_page' in request.form and request.form['two_per_page'] == 'true':
                for i in range(0, len(df_urls), 2):
                    # Fetch data for the first entry
                    row1 = df_urls.iloc[i]
                    photo1 = row1['Index']
                    object_id1 = row1['ObjectID']
                    chosen_headers1 = ", ".join([str(row1[header]) for header in selected_headers if header != 'ObjectID' and header != 'URLs'])
                    comment_string1 = f"Photograph {object_id1} - {chosen_headers1}"
                    file_path1 = images_df.loc[i, 'File_Path']

                    # Fetch data for the second entry
                    if i+1 < len(df_urls):
                        row2 = df_urls.iloc[i+1]
                        photo2 = row2['Index']
                        object_id2 = row2['ObjectID']
                        chosen_headers2 = ", ".join([str(row2[header]) for header in selected_headers if header != 'ObjectID' and header != 'URLs'])
                        comment_string2 = f"Photograph {object_id2} - {chosen_headers2}"
                        file_path2 = images_df.loc[i+1, 'File_Path']
                    else:
                        # If the number of entries is odd, duplicate the last entry
                        row2 = row1
                        photo2 = row2['Index']
                        object_id2 = row2['ObjectID']
                        chosen_headers2 = ", ".join([str(row2[header]) for header in selected_headers if header != 'ObjectID' and header != 'URLs'])
                        comment_string2 = f"Photograph {object_id2} - {chosen_headers2}"
                        file_path2 = images_df.loc[i, 'File_Path']

                    # Open and process the first image
                    with Image.open(file_path1) as img1:
                        width1, height1 = img1.size
                        if hasattr(img1, '_getexif'):
                            exif1 = img1._getexif()
                            if exif1:
                                orientation1 = exif1.get(274)
                                if orientation1 in [5, 6, 7, 8]:
                                    width1, height1 = height1, width1  # Swap width and height
                                    angle1 = -90
                                else:
                                    angle1 = 0
                        else:
                            angle1 = 0

                    # Open and process the second image
                    with Image.open(file_path2) as img2:
                        width2, height2 = img2.size
                        if hasattr(img2, '_getexif'):
                            exif2 = img2._getexif()
                            if exif2:
                                orientation2 = exif2.get(274)
                                if orientation2 in [5, 6, 7, 8]:
                                    width2, height2 = height2, width2  # Swap width and height
                                    angle2 = -90
                                else:
                                    angle2 = 0
                        else:
                            angle2 = 0

                    # Build the TeX content using the two-page section template
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

                    # Append the section content to the overall TeX content
                    tex_content += section_content

            else:
                for index, row in df_urls.iterrows():
                    # Check if the index exists in images_df
                    if index < len(images_df):
                        # Fetch data from df_urls
                        photo = row['Index']
                        object_id = row['ObjectID']
                        chosen_headers = ", ".join([str(row[header]) for header in selected_headers if header != 'ObjectID' and header != 'URLs'])
                        comment_string = ""
                        comment_string += f"Photograph {object_id} - {chosen_headers}"

                        # Fetch data from images_df
                        file_path = images_df.loc[index, 'File_Path']
                        with Image.open(file_path) as img:
                            print(f"Opening {file_path}")
                            
                            width, height = img.size
                            
                            # Check if the image has orientation metadata
                            if hasattr(img, '_getexif'):
                                exif = img._getexif()
                                if exif:
                                    orientation = exif.get(274)
                                    if orientation in [5, 6, 7, 8]:
                                        # Swap width and height
                                        width, height = height, width
                                        angle = -90
                                        img_width = 0.37
                                    else:
                                        angle = 0
                                        img_width = 0.42
                            else:
                                angle = 0
                                img_width = 0.42

                        # Build the TeX content using the section template
                        section_content = a4section_template.replace("#photopath1#", file_path)\
                                                            .replace("#comment_string#", comment_string)\
                                                            .replace("#angle#", str(angle))\
                                                            .replace("#img_width#", str(img_width))\
                                                            .replace("#project#", project)\
                                                            .replace("#client#", client)\
                                                            .replace("#notes#", notes)\
                                                            .replace("#appendix#", appendix)

                        # Append the section content to the overall TeX content
                        tex_content += section_content

            # Close the TeX document
            tex_content += r"\end{document}"

            # Write the generated TeX content to a file
            with open("output.tex", "w") as tex_file:
                tex_file.write(tex_content)
            






















# /////////////////////////////////////////////////WORKING ON/////////////////////////////////////


        
        