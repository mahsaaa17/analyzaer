import os
import io
import pandas as pd
try:
    from docx import Document
except ImportError:
    Document = None

def process_uploaded_file(file_name, file_data):
    extension = os.path.splitext(file_name)[1].lower()
    
    if extension == '.docx':
        if Document is None:
            raise ImportError("python-docx is not installed.")
        doc = Document(io.BytesIO(file_data))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        
        rows = []
        for table in doc.tables:
            for row in table.rows:
                cells = [cell.text.strip() for cell in row.cells]
                if len(cells) >= 3:
                    rows.append(cells[:3])
        
        df = pd.DataFrame(rows, columns=['متن مصاحبه', 'مفاهیم معنادار', 'کد'])
        df = df[df['مفاهیم معنادار'].astype(str).str.strip() != 'مفاهیم معنادار'].reset_index(drop=True)
        return df
        
    elif extension == '.xlsx':
        excel_data = pd.read_excel(io.BytesIO(file_data), sheet_name=None)
        frames = []
        for sheet_name, sheet_df in excel_data.items():
            sheet_df = sheet_df.dropna(how='all')
            sheet_df['نام برگه'] = sheet_name
            frames.append(sheet_df)
        df = pd.concat(frames, ignore_index=True)
        return df
    else:
        raise ValueError("Unsupported file extension. Only .docx and .xlsx are supported.")
