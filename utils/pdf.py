from fpdf import FPDF
import logging

from .summarizer import CategoryEnum


def generate_pdf(input_df):
    # Initialize PDF
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "EMNLP 2024 Paper Abstracts", 0, 1, "C")

    # Configure PDF styles
    pdf.set_font("Arial", "", 12)
    pdf.set_left_margin(15)
    pdf.set_right_margin(15)

    # Get unique categories
    categories = input_df['Category'].unique()
    input_df['HasAbstract'] = ~input_df['Abstract'].isnull()

    # Loop through each category
    for category_idx, category in enumerate(categories):
        # Filter and sort papers by score within the category
        category_df = input_df[input_df['Category'] == category].sort_values(by=["HasAbstract", "Score"],
                                                                             ascending=[False, False])

        # If no category prediction then set uncategorized
        if category is None:
            category_df = input_df[input_df['Category'].isnull()]
            category = "Uncategorized"
        else:
            category = CategoryEnum(category).value

        # Add category title
        if category_idx > 0:
            pdf.add_page()  # Add new page for each category if desired
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 8, f"{category}", 0, 1, "C")
        pdf.ln(5)  # Line break

        # Loop through each paper in the category
        for index, row in category_df.iterrows():
            try:
                # Add a page break if needed
                if pdf.get_y() > 240:
                    pdf.add_page()

                # Title
                pdf.set_font("Arial", "B", 10)
                pdf.multi_cell(0, 5, f"{index + 1}. {row['Original Title']}\n")

                # Abstract
                pdf.set_font("Arial", "", 8)
                if row["Summary"]:
                    pdf.multi_cell(0, 5, f"{row['Summary']}\n")

                # URL
                if row["PaperUrl"]:
                    pdf.set_font("Arial", "I", 8)
                    pdf.multi_cell(0, 5, f"{row['PaperUrl']}")

                # Spacer between entries
                pdf.cell(0, 5, "", 0, 1)
            except Exception as e:
                logging.error(f"Error processing paper {index + 1} in category {category}: {e}")

    # Save PDF
    pdf_output_path = "./data/emnlp_2024_summary.pdf"
    pdf.output(pdf_output_path)
    logging.info(f"PDF generated and saved as {pdf_output_path}")
