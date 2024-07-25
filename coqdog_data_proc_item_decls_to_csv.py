import re
import csv
import os

"""
Auther: @Amer N. Tahat, Collins Aerospace, The script is to ensure that all types of declarations (Definitions, Fixpoints, and Inductives) are extracted
-- adjusting the regular expression to capture the entire body of the declarations. 2023 all rights reserved.
"""


def extract_all_declarations_and_write_to_csv_enhanced(coq_file_path, csv_file_path):
    """
    Extracts all types of declarations (Definitions, Fixpoints, and Inductives) from a Coq file
    and writes them to a CSV file. This function is enhanced to ensure that all 21 expected
    declarations are captured accurately.

    Args:
    coq_file_path (str): The path to the Coq file.
    csv_file_path (str): The path to the output CSV file.
    """
    # Enhanced regular expression pattern to match each declaration type till the next declaration or end of file
    pattern = r"(Definition|Fixpoint|Inductive)\s+(\w+)((?:.|[\r\n])*?)(?=\n(?:Definition|Fixpoint|Inductive|$))"

    # Read the contents of the Coq file
    with open(coq_file_path, 'r') as file:
        file_content = file.read()

    # Find matches for all declarations
    matches = re.findall(pattern, file_content, re.DOTALL)

    # Prepare data for CSV
    csv_data = []
    for match in matches:
        declaration_keyword, item_name, item_body = match
        int_label = {"Definition": 3, "Fixpoint": 4, "Inductive": 5}.get(declaration_keyword, 0)
        csv_data.append([item_name, item_body.strip(), int_label, declaration_keyword])

    # Write data to CSV file
    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["item-name", "item-body", "int-label", "label"])
        writer.writerows(csv_data)

    print('csv is written')

    return len(csv_data)  # Return the number of extracted declarations for verification


# Enhanced extraction and writing to CSV
# enhanced_csv_file_path = './declarations_enhanced.csv'
# num_declarations_extracted_enhanced = extract_all_declarations_and_write_to_csv_enhanced(coq_file_path_to_extract,
#                                                                                         enhanced_csv_file_path)
# num_declarations_extracted_enhanced


# Extract all declarations and write to CSV, and verify the number of extracted items

def main():
    coq_files_names = [
        "./AbstractedTypes.v", "./AllMapped.v", "./AM_Monad.v", "./AM_St.v", "./Anno_Term_Defs.v",
        "./Appraisal_AltImpls_Eq.v", "./Appraisal_Defs.v", "./Appraisal_Evidence.v", "./Appraisal_IO_Stubs.v",
        "./Appraisal_Semantics.v", "./Appraisal.v", "./AutoApp.v", "./Auto.v", "./Axioms_Io.v", "./BS.v",
        "./ConcreteEvidence.v", "./Copland_AC.v", "./CopParserQC.v", "./CopParser.v", "./Cvm_Impl.v",
        "./Cvm_Monad.v", "./Cvm_Run.v", "./CvmSemantics.v", "./Cvm_St.v", "./Defs.v", "./Demo_AM.v", "./Disclose.v",
        "./Eqb_Evidence.v", "./EqClass.v", "./Event_system.v", "./Evidence_Bundlers.v", "./Example_Phrases_Admits.v",
        "./Example_Phrases_Demo_Admits.v", "./Example_Phrases_Demo.v", "./Example_Phrases.v", "./External_Facts.v",
        "./Extraction_All.v", "./Extraction_Cvm_Cake.v", "./Helpers_Appraisal.v", "./Helpers_CvmSemantics.v",
        "./Helpers_MonadAM.v", "./Impl_appraisal_alt.v", "./Impl_appraisal.v", "./IO_Stubs.v", "./IO_Type.v",
        "./LTS.v", "./Main.v", "./Manifest_Orig.v", "./Manifest.v", "./Maps.v", "./MonadLaws.v", "./More_lists.v",
        "./OptMonad_Coq.v", "./Params_Admits.v", "./Preamble.v", "./privPolicy.v", "./StMonad_Coq.v",
        "./StructTactics.v", "./Term_Defs_Core.v", "./Term_Defs.v", "./Term_system.v", "./Term.v", "./Test_Extract.v",
        "./Trace.v"]

    coq_file_path_to_extract = './Anno_Term_Defs.v'
    csv_file_path_for_declarations = './Anno_Term_Defs_dcls.csv'
    num_declarations_extracted = extract_all_declarations_and_write_to_csv_enhanced(coq_file_path_to_extract,
                                                                           csv_file_path_for_declarations)
    num_declarations_extracted


if __name__ == "__main__":
    main()
