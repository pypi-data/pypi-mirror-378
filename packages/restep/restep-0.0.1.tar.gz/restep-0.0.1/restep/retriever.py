import transformers
import torch
import gc
import json
import difflib
from transformers import BitsAndBytesConfig, pipeline

def instantiate_pipeline_llama(access_token):
    """
    Loads Llama 3.1 8B Instruct with 4-bit quantization to fit on a 16 GB GPU.
    """
    transformers.set_seed(42)
    model_id = "meta-llama/Meta-Llama-3.1-8B-Instruct"

    quant_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
    )

    pipe = pipeline(
        task="text-generation",
        model=model_id,
        tokenizer=model_id,
        token=access_token,
        torch_dtype=torch.bfloat16,          # compute dtype (separate from quant cfg)
        trust_remote_code=True,              # ← set here, NOT in model_kwargs
        device_map="auto",
        model_kwargs={
            "quantization_config": quant_config,
            "low_cpu_mem_usage": True,
            "use_cache": True,
        },
    )

    # keep context reasonable; you don't need 128k on a 16 GB card
    pipe.tokenizer.model_max_length = 8192
    return pipe



def retriever(text, pipe):
    '''

    Parameters:

    
    Returns:
    str: Labels of topic models
    '''
    
    # Enhanced prompt structure with clearer instructions
    messages = [
        {"role": "system", "content": (
            "You are a useful assistant to an early stage developer working for a renewable energy utility firm. "
            "You are looking through a provided chunk of text from local government documents."
            "Your job is to extract specific texts that will be of interests to me as an early stage developer. "
            "These could include ordinances, regulations or incentives towards utilities seeking to invest in renewables "
            "as well as comments, complaints, appraisals or feedback by authorities or residents about utility companies or potential renewable energy investments."
            "Your job is to retrieve the specific texts from the provided chunk. If there is None, strictly return NONE. Let's think about this carefully step-by-step."
            'Strictly return it in the following format: {"Thought":"<your thought>","text":<retrieved text>}'
            "Below are some provided examples:"
        )}
    ]
    example_1='''The Clerk administered the oath to David Levy, an attorney with Baird Holm LLP and attorney for the applicant,
    and Matt Jones, developer for the Center of Public Health.
    Levy presented and read quotes from the letters of support into the record (Exhibit 5).
    Jones presented a power point presentation about the project (Exhibit 6)
    Flowerday inquired about hiring local union labor. Jones stated the company would work with the community
    but was unsure of the company's policy. Flowerday noted that a labor agreement should be considered. Levy
    stated Health Center has worked with union labor in the past.
    Schulte and Levy discussed how the project could affect property valuations and revenue collections of the
    property and the surrounding area.
    Yoakum inquired about how the applicant would respond to noise level complaints. Levy stated the project
    would stay within the requirements maintained by the County and follow that process. Yoakum asked if the
    landowners who are leasing the land would continue to use the property that is not being used in the project.
    Jones stated in the lease agreement the property owners have the right to exclude property. Yoakum stated
    support for the project to use union employees. 
    '''
    answer_1='''{"Thought":"This text summarizes a discussion between local officials and representatives regarding the Center of Public Health project, 
    focusing on community engagement, labor agreements, property impacts, and noise concerns. None of these are remotely related to energy.",
    "text":"NONE"}
    '''
    example_2='''
    Recommendation from the Southeast Nebraska Development District (SENDD) to award a contract
    through the Lancaster County Owner Occupied Rehabilitation Housing Program for Project 020 to MIT
    Contracting in the amount of $13,115.30 to replace kitchen sink plumbing pipes, install four more Ibeams at the foundation wall for support, replace exterior front steps, install attic insulation, fix double
    taps in a breaker box, and repair the garage door.

    The Clerk administered the oath to George Wesselhoft, Planning Department Planner. Wesselhoft presented a
    map of the area (Exhibit 3) and described the project and the special permit. He noted the 2050
    Comprehensive Plan supports renewable energy. Wesselhoft noted the applicant submitted a complete
    application that met all requirements and included additional documents that include a sight line study, an
    environmental compliance document, an emergency action plan, and an economic impact study. He provided
    and reviewed requirements and criteria needed to receive a solar energy permit from the summary report (see
    agenda). Wesselhoft stated the Planning Commission voted and made a motion to approve on December 18,
    2024, that included changing the setbacks from 50 feet to 100 feet from the property line of any nonparticipating property without a dwelling and changing the site plan from 100 feet setbacks to 250 feet setbacks
    from the property line of any non-participating property with a dwelling on any side of the property facing solar
    panels. Wesselhoft stated a memo was submitted to the Board for clarification after the January 9, 2025,
    briefing with reference to a prior solar project, Special Permit 21042 Salt Creek Solar (Exhibit 4).
    Schulte asked for clarification about the Salt Creek project setbacks. Wesselhoft stated there was an increase
    from 50 feet to 100 feet from the property line of any non-participating property without a dwelling and an
    increase from 100 feet to 250 feet of setbacks from the property line for any non-participating property with a
    dwelling. The site plan replaces 300-foot setbacks for non-participating properties with a dwelling that are
    currently in the Community Unit Plan (CUP). Schulte noted the current properties are not in a Community Unit
    Plan, but the Board could amend the permit to include the CUP setbacks. Wesselhoft stated yes. Schulte
    asked if there were any other amendments that were included in the Salt Creek Permit. Wesselhoft stated an
    amendment is included that only evergreen trees be used in the screening landscaping. Schulte asked for
    clarification for if only four properties are surrounded by the project. Wesselhoft stated there are four nonparticipating properties and pointed out the locations on the map (Exhibit 3). 
    '''
    text_2='''
    The Clerk administered the oath to George Wesselhoft, Planning Department Planner. Wesselhoft presented a
    map of the area (Exhibit 3) and described the project and the special permit. He noted the 2050
    Comprehensive Plan supports renewable energy. Wesselhoft noted the applicant submitted a complete
    application that met all requirements and included additional documents that include a sight line study, an
    environmental compliance document, an emergency action plan, and an economic impact study. He provided
    and reviewed requirements and criteria needed to receive a solar energy permit from the summary report (see
    agenda). Wesselhoft stated the Planning Commission voted and made a motion to approve on December 18,
    2024, that included changing the setbacks from 50 feet to 100 feet from the property line of any nonparticipating property without a dwelling and changing the site plan from 100 feet setbacks to 250 feet setbacks
    from the property line of any non-participating property with a dwelling on any side of the property facing solar
    panels. Wesselhoft stated a memo was submitted to the Board for clarification after the January 9, 2025,
    briefing with reference to a prior solar project, Special Permit 21042 Salt Creek Solar (Exhibit 4).
    Schulte asked for clarification about the Salt Creek project setbacks. Wesselhoft stated there was an increase
    from 50 feet to 100 feet from the property line of any non-participating property without a dwelling and an
    increase from 100 feet to 250 feet of setbacks from the property line for any non-participating property with a
    dwelling. The site plan replaces 300-foot setbacks for non-participating properties with a dwelling that are
    currently in the Community Unit Plan (CUP). Schulte noted the current properties are not in a Community Unit
    Plan, but the Board could amend the permit to include the CUP setbacks. Wesselhoft stated yes. Schulte
    asked if there were any other amendments that were included in the Salt Creek Permit. Wesselhoft stated an
    amendment is included that only evergreen trees be used in the screening landscaping. Schulte asked for
    clarification for if only four properties are surrounded by the project. Wesselhoft stated there are four nonparticipating properties and pointed out the locations on the map (Exhibit 3). '''

    answer_2 = f'{{"Thought":"Starting from the 2nd paragraph, the text describes a meeting where planner George Wesselhoft presented details about a solar energy project\'s permit application, reviewed requirements and setback adjustments, and addressed specific questions from Board member Schulte about setbacks, landscaping, and surrounding non-participating properties, which is highly relevant to you as a potential renewable energy developer looking to invest in this community.","text":"{text_2}"}}'

    example_3='''Sheriff Matt Hassel presented an Agreement between Central Square Technologies, LLC, and Marshall
    County Sheriff's Office. He and IT Director Michael Marshall explained that four additional functions
    will be added. Foremost, all data will be secured in the cloud, which is the safest place to store and
    back up data. Contains Citizens Reporting, which allows citizens access to report their criminal
    complaints directly to the CentralSquare software which expedites the reporting. The County will have
    access to our backed-up data. Eliminates the need to use VPNs for our Mobile Data Terminal. The
    initial cost is $25,000 and is available in the Sheriff's current budget. In 2025, the cost will be
    $123,364.14 and when the project is fully completed, the cost will increase to $168,075 in 2026.
    Mike Burroughs moved, second by Kevin Overmyer, to approve the Agreement between Central
    Square Technologies LLC and the Marshall County Sheriff's Office as presented.
    Motion carried 3-0.

    Councilman Peter commented about the amount of noise brought about from the construction of new windmills by NextEra Energy. 
    He questioned why residents of this community have to has to be the ones who suffer such "unbearable" noise 
    just so that they could supply energy to other nearby towns. 


    Marshall County Community Foundation (MCCF) Executive Director Linda Yoder and
    Shawn Peterson Community Redevelopment Partners provided information about the Lilly
    Endowment Giving Indiana Funds for Tomorrow (GIFT) VIII Community Leadership Phase 2
    Implementation Grant. In April 2023, MCCF submitted a concept paper for the Community
    Leadership Phase 2 Implementation grant and was invited to submit a final proposal, which is due
    September 6th. The request is for $5 million to establish a countywide Community Development
    Corporation (CDC) and a Community Development Loan Fund (CDLF). The CDC is a 501(c)(3)
    nonprofit organization dedicated to developing affordable housing across Marshall County. The CDLF
    is a flexible loan fund established to catalyze new housing development in Marshall County. It will
    provide short-term, low-cost flexible financing to cities/towns, the CDC, or other nonprofit developers. 
    '''

    text_3='''Councilman Peter commented about the amount of noise brought about from the construction of new windmills by NextEra Energy. 
    He questioned why residents of this community have to has to be the ones who suffer such "unbearable" noise 
    just so that they could supply energy to other nearby towns.'''

    answer_3 = f'{{"Thought":"The paragraph about concilman\'s Peters complaint about noise brought about from the construction of new wind mills is highly relevant to your potential renewable energy investments in this area. It seems that Peter is showing signs of resentment towards renewable energy, and this could negatively impact your ability to launch successful renewable energy developments in this area.","text":"{text_3}"}}'



    example_4='''The community hosted "Go Green Day", where local high schools learned about the importance of energy conversation. Allentown High School invited 
    Dr. Benjamin from the National Renewable Energy Laboratory to share about the future of renewable energy and Dr. Jun from the National Oceanic and Atmospheric Administration
    to learn about the importance of energy conservation for the climate. 
    '''

    answer_4 = f'{{"Thought":"The paragraph about the successful GO GREEN DAY is likely to be relevant to your potential investment in renewable energy in this community. The community has a positive attitude towards renewable energy, and this is useful information is indicative of potential support from the community towards renewable energy efforts.","text":"{example_4}"}}'

    example_5=''' Invenergy Project Developer Ethan Sternberg presented a PowerPoint presentation on the Tamarack
    Solar Project. He explained Marshall County was selected because of the access to the grid, it is a
    consistent solar resource, the demand for electricity, and interested landowners. The project will
    provide 150MW powering 29,000 homes, utilize advanced solar technology, connect to the Burr Oak
    Substation. Twelve families have signed leases for approximately 1,435 acres within the fence.
    Invenergy has invested $1.45 million to date. The project details are based on the Marshall County
    solar ordinance. He stated there will be an average of 175 construction jobs at peak construction.
    Invenergy's $250 million capital investment will contribute over $40 million in property tax payments
    and $60 million in payments to participating landowners. Invenergy will not seek a tax abatement.'''

    answer_5 = f'{{"Thought":"The paragraph talks about a utility firm, Invenergy, planning to invest in an energy project in the area. This could be of interest to you for many reasons. This could include potential competition from a competing utility or perhaps if they are successful, it likely resonates their openness to renewable energy. My suggestion is to follow this development closely.","text":"{example_5}"}}'

    example_6=''' Begley asked all opponents to stand. He argued that landowners will face financial losses if the project is constructed. 
    He noted the project is not in compliance with local zoning and would present risk because there are times it is not sunny. 
    He argued the project breaks state law and encouraged Board members to follow the law. 
    Solar panels are not in harmony with the surrounding area and are not an agricultural use.
    
    The Clerk administered the oath to the next testifiers called forward.
    Torri Lienemann, County resident, reviewed a power point presentation (Exhibit 12). She asked for proponents of the project to stand. She displayed photos of the location of her ranch and the solar project. She discussed the risk to birds due to the "lake effect hypothesis."
    Skylar Lienemann, County resident, continued to review the power point presentation and discussed risks to migratory birds. Torri Lienemann provided more details of a study on the potential danger to birds.
    Kim Topp, County resident and real estate broker, presented documents to the Board (Exhibit 13). She discussed the effects the solar project could have on property values.
    Bruce Topp, County resident, presented documents (Exhibit 14) and expressed opposition to the solar project due to the potential effect on property values. He said this could have a negative effect on County property tax revenues.
    Drew Topp, County resident, presented pictures of his home and land (Exhibit 15). He argued the solar project is not in harmony with the surrounding area. He complained about the potential noise and light pollution.'''

    answer_6 = f'{{"Thought":"Most of the text seems to be residents voicing their opposition towards a solar project and discussing their perceived negative repurcusssions towards their community. These include effects on birds and property values.","text":"{example_6}"}}'

    prompt=f'''Let's think about this carefully step-by-step. Your job is to retrieve the specific texts from the provided chunk that will be of interest to me as an early stage
    developer seeking to potential set up renewable energy infrastructure (e.g., solar farm and wind mills) in this community. Strictly return it in the format: {{"Thought":"<your thought>","text":<retrieved text>}} 
    
    Here is my text:{text}'''
    # Explicit instruction for labeling
    messages.append({"role": "user", "content": example_1})
    messages.append({"role": "assistant", "content": answer_1})
    messages.append({"role": "user", "content": example_2})
    messages.append({"role": "assistant", "content": answer_2})
    messages.append({"role": "user", "content": example_3})
    messages.append({"role": "assistant", "content": answer_3})
    messages.append({"role": "user", "content": example_4})
    messages.append({"role": "assistant", "content": answer_4})
    messages.append({"role": "user", "content": example_5})
    messages.append({"role": "assistant", "content": answer_5})
    messages.append({"role": "user", "content": example_6})
    messages.append({"role": "assistant", "content": answer_6})

    messages.append({"role": "user", "content": prompt})



    outputs = pipe(
        messages,
        max_new_tokens=1500,
        do_sample=False,
        temperature=0,
        pad_token_id=pipe.tokenizer.pad_token_id,
        eos_token_id=pipe.tokenizer.eos_token_id,
        
    )

    # Clear cache to free up GPU memory
    answer=outputs[0]["generated_text"][-1]["content"]
    # print("answer",answer)
    # Return the generated label from the output
    gc.collect()
    torch.cuda.empty_cache()
    del outputs, pipe
    return answer

def extract_retrieved_text(response_str):
    '''
    Converts the string response from model output into a dictionary
    and retrieves the text associated with the "text" key.

    Parameters:
        response_str (str): String representation of a dictionary in format:
            '{"Thought":"<thought>", "text":"<retrieved text>"}'

    Returns:
        str: The retrieved text content.
    '''
    try:
        # Safely convert string to dictionary
        response_dict = json.loads(response_str)
        return response_dict.get("text", None)
    
    except json.JSONDecodeError:
        # Return None if string format is invalid
        return None


def remove_overlap_and_join(chunks, separator="..."):
    """
    Removes overlapping text from a list of text chunks and joins them smoothly.

    Args:
        chunks (list[str]): List of overlapping text chunks.
        separator (str): Separator to use between chunks.

    Returns:
        str: Joined string with overlaps removed.
    """
    if not chunks:
        return ""

    merged_text = chunks[0]

    for next_chunk in chunks[1:]:
        # Find overlap using SequenceMatcher
        s = difflib.SequenceMatcher(None, merged_text, next_chunk)
        match = s.find_longest_match(len(merged_text)//2, len(merged_text), 0, len(next_chunk)//2)

        if match.size > 0:
            # Append non-overlapping portion only
            merged_text += separator + next_chunk[match.b + match.size:].lstrip()
        else:
            # No meaningful overlap found; concatenate directly
            merged_text += separator + next_chunk

    # print(merged_text)
    return merged_text

import gc, torch

def summarize_text(text: str, pipe, *, max_input_tokens: int = 3800, max_new_tokens: int = 300) -> str:
    """
    One concise paragraph. Neutral and factual.
    - Preserve concrete details (names, dates, MW/acres/$, votes/ordinances/permits/moratoria/setbacks).
    - When objections appear (wildlife/birds, noise, property values, etc.), attribute them to speakers; do not infer motives.
    - No lists, no sections—just a single paragraph.
    """

    # (Optional) hard trim very long inputs by tokens to avoid OOM/context overflow
    tok = pipe.tokenizer
    ids = tok(text, add_special_tokens=False).input_ids
    if len(ids) > max_input_tokens:
        ids = ids[:max_input_tokens]
        text = tok.decode(ids, skip_special_tokens=True)

    messages = [
        {"role": "system", "content":
         ("Summarize the user's text into ONE concise paragraph. Be strictly factual and neutral. "
          "Preserve concrete details (names, dates, quantities like MW/acres/$, and any formal actions such as votes, ordinances, permits, "
          "moratoria, setbacks). When opinions or objections appear, attribute them to the speaker or group; do not add or infer motives. "
          "Do not include lists or headings—just one paragraph.")},
        {"role": "user", "content": f"Text:\n{text}"}
    ]

    out = pipe(
        messages,
        max_new_tokens=max_new_tokens,
        do_sample=False,
        temperature=0.0,
        pad_token_id=getattr(pipe.tokenizer, "pad_token_id", None),
        eos_token_id=getattr(pipe.tokenizer, "eos_token_id", None),
    )

    summary = out[0]["generated_text"][-1]["content"].strip()

    # light cleanup; keep pipeline for reuse
    del out, pipe
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    return summary
