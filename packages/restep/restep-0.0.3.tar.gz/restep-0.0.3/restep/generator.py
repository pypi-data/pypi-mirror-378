import transformers
import torch
import gc
import json
import difflib



def generator(text, pipe):
    """
    Returns STRICT JSON:
      {"Sentiment": "POSITIVE"|"NEGATIVE"|"NEUTRAL", "Summary": "<concise factors>"}
    Uses your original few-shots unchanged; adds investor-centric rubric + neutral→negative override on hard blockers.
    """
    import gc, torch, json

    # Terms that, from an investor lens, should never be treated as neutral if present
    NEG_TRIGGERS = [
        "moratorium","ban","prohibit","prohibition","deny","denied","rescinded",
        "increase setback","increased setback","larger setback","setbacks",
        "minimum lot size","larger lot","petition","referendum","lawsuit","litigation","appeal",
        "wildlife","bird","migratory","noise","glare","shadow flicker","property values","viewshed"
    ]

    system = """You are advising an early-stage developer at a renewable energy utility firm.
Classify the community stance toward NEW renewable investments from an INVESTOR RISK perspective.

RUBRIC (prioritize enforceable actions over commentary):
- NEGATIVE (default if material friction exists): moratoriums/bans/denials; moves toward them; stricter siting (bigger setbacks/lot sizes);
  litigation threats/appeals/petitions; nuisance/impact objections (noise, glare/flicker, wildlife/birds, viewshed, property values, tax-revenue fears);
  expensive studies/mitigations/bonds imposed. These raise cost, delay, or denial risk.
- POSITIVE: approvals/votes passed; enabling overlays/code updates that make siting easier; incentives/grants; supportive officials.
- NEUTRAL: only if the text lacks clear enabling actions AND lacks clear friction. Ambiguous “concerns” without action do NOT outweigh restrictions.

Note:
1. Be careful in detecting not-in-my-backyard (NIMBY) situations, where the community may seem to be friendly and open to certain demands (e.g., visual concerns),
but are using 'excuses' like visual concerns or wildlife damage as a pretext to oppose renewables without explicitly having to say so.  
2. Investments towards solar energy, any green iniatives or anything that could potential encourage future solar investment should be viewed as a positive!
3. Positive comments (e.g., desire for solar and EVs) made towards renewables should be considered POSITIVE. 
4. Negative comments or anti-renewable commments should always be considered NEGATIVE. 

Output STRICT JSON only:
{"Sentiment": "POSITIVE"|"NEGATIVE"|"NEUTRAL", "Summary": "<concise summary detailing specific influencing factors>"}"""

    # --- your original few-shots (unchanged) ---
    example_1 = """The Clerk administered the oath to David Levy, an attorney with Baird Holm LLP and attorney for the applicant,
and Matt Jones, developer for the Panama Energy Center.
Levy presented and read quotes from the letters of support into the record (Exhibit 5).
Jones presented a power point presentation about the project (Exhibit 6)
Flowerday inquired about hiring local union labor. Jones stated the company would work with the community
but was unsure of the company’s policy. Flowerday noted that a labor agreement should be considered. Levy
stated NextEra has worked with union labor in the past.
Schulte and Levy discussed how the project could affect property valuations and revenue collections of the
property and the surrounding area.
Yoakum inquired about how the applicant would respond to noise level complaints. Levy stated the project
would stay within the requirements maintained by the County and follow that process. Yoakum asked if the
landowners who are leasing the land would continue to use the property that is not being used in the project.
Jones stated in the lease agreement the property owners have the right to exclude property. Yoakum stated
support for the project to use union employees."""
    answer_1 = (
        '{"Sentiment": "NEGATIVE", '
        '"Summary": "Material concerns on noise and property values with pressure for a labor agreement—added cost/conditions and potential opposition."}'
    )

    example_2 = """The community hosted "Go Green Day", where local high schools learned about the importance of energy conservation. Allentown High School invited 
Dr. Benjamin from the National Renewable Energy Laboratory to share about the future of renewable energy and Dr. Jun from the National Oceanic and Atmospheric Administration
to learn about the importance of energy conservation for the climate."""
    answer_2 = (
        '{"Sentiment": "POSITIVE", '
        '"Summary": "Active sustainability culture and partnerships with NREL/NOAA suggest receptiveness and smoother permitting."}'
    )

    example_3 = """Begley asked all opponents to stand. He argued that landowners will face financial losses if the project is constructed. 
He noted the project is not in compliance with local zoning and would present risk because there are times it is not sunny. 
He argued the project breaks state law and encouraged Board members to follow the law. 
Solar panels are not in harmony with the surrounding area and are not an agricultural use.

The Clerk administered the oath to the next testifiers called forward.
Torri Lienemann, County resident, reviewed a power point presentation (Exhibit 12). She asked for proponents of the project to stand. She displayed photos of the location of her ranch and the solar project. She discussed the risk to birds due to the "lake effect hypothesis."
Skylar Lienemann, County resident, continued to review the power point presentation and discussed risks to migratory birds. Torri Lienemann provided more details of a study on the potential danger to birds.
Kim Topp, County resident and real estate broker, presented documents to the Board (Exhibit 13). She discussed the effects the solar project could have on property values.
Bruce Topp, County resident, presented documents (Exhibit 14) and expressed opposition to the solar project due to the potential effect on property values. He said this could have a negative effect on County property tax revenues.
Drew Topp, County resident, presented pictures of his home and land (Exhibit 15). He argued the solar project is not in harmony with the surrounding area. He complained about the potential noise and light pollution."""
    answer_3 = (
        '{"Sentiment": "NEGATIVE", '
        '"Summary": "Coordinated opposition with zoning/legal attacks and concerns over wildlife, property values, taxes, and nuisance—high siting friction."}'
    )

    example_4 = """The town council has openly expressed concerns about birds and other wildlife being affected by windmills. They say that windmills could hit and kill birds. 
    Councilman Jeffrey agreed, and said that he is concerned for the environment and therefore feel that windmills should have strict rules. Others commented that the windmills 
    may destroy the towns beautiful scenery. Unless they can promise to get it below a certain height, they are open to having windmills in town. """
    answer_4 = (
        '{"Sentiment": "NEGATIVE", '
        '"Summary": "The community\'s expression of concern surrounding the destruction of birds and scenery seem to be a distraction and pretext (NIMBY) of resistance towards potential investment of renewables in the area."}'
    )
    # -----------------------------------------

    messages = [{"role": "system", "content": system}]
    messages += [
        {"role": "user", "content": example_1}, {"role": "assistant", "content": answer_1},
        {"role": "user", "content": example_2}, {"role": "assistant", "content": answer_2},
        {"role": "user", "content": example_3}, {"role": "assistant", "content": answer_3},
        {"role": "user", "content": example_4}, {"role": "assistant", "content": answer_4},
    ]

    user_prompt = (
        "Classify the following text strictly from an INVESTOR perspective using the rubric above. "
        "Return ONLY the required JSON.\n\n"
        f"Text:\n{text}\n"
    )
    messages.append({"role": "user", "content": user_prompt})

    outputs = pipe(
        messages,
        max_new_tokens=600,
        do_sample=False,
        temperature=0,
        pad_token_id=getattr(pipe.tokenizer, "pad_token_id", None),
        eos_token_id=getattr(pipe.tokenizer, "eos_token_id", None),
    )

    # Extract model output text
    try:
        out = outputs[0]["generated_text"][-1]["content"]
    except Exception:
        try:
            out = outputs[0]["message"]["content"]
        except Exception:
            out = str(outputs)

    # --- Post-hoc investor override: if model says NEUTRAL but hard blockers are in the text, flip to NEGATIVE ---
    try:
        obj = json.loads(out)
        if obj.get("Sentiment") == "NEUTRAL":
            tl = text.lower()
            if any(trig in tl for trig in NEG_TRIGGERS):
                obj["Sentiment"] = "NEGATIVE"
                if "Summary" in obj and obj["Summary"]:
                    obj["Summary"] += " (Material siting friction present.)"
                else:
                    obj["Summary"] = "Material siting friction (e.g., bans/moratoriums/stricter setbacks/petitions)."
                out = json.dumps(obj)
    except Exception:
        pass

    # Cleanup
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    del outputs, pipe
    return out
