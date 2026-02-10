# prompt_builder.py
# Prompts tuned for FLUX: clear, literal outfit description first.

def build_outfit_prompt(outfit, gender):
    top = outfit["top"]["name"]
    bottom = outfit["bottom"]["name"]
    shoes = outfit["shoes"]["name"] if outfit["shoes"] else "matching shoes"

    if gender == "Men":
        subject = "male fashion model, masculine, full body"
        negative_gender = "woman, female, feminine, breasts"
    else:
        subject = "female fashion model, feminine, full body"
        negative_gender = "man, male, masculine, beard"

    # FLUX follows the start of the prompt best; put exact clothing first
    prompt = (
        f"{top} and {bottom} with {shoes}. "
        f"Full body fashion photo of {subject} wearing {top}, {bottom}, {shoes}. "
        f"Neutral grey studio background, standing, soft lighting, catalog style, sharp, high quality."
    )

    negative_prompt = (
        f"blurry, low quality, distorted, extra limbs, bad anatomy, "
        f"real face, smile, portrait, close-up, {negative_gender}, "
        f"outdoor, crowd, wrong clothes, nude"
    )

    return {
        "prompt": prompt.strip(),
        "negative_prompt": negative_prompt.strip(),
    }
