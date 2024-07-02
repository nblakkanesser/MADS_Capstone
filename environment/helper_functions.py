import json
def create_prompt_response(row, target):
    """
    Parses the synthetic data into GPT format
    """
    if target == 'endpoint':
        dict = {'prompt': row['query'],
                'completion':f"endpoint: {row['api_call.endpoint']}"}
    if target == 'parkcode':
        dict = {'prompt': row['query'],
                'completion':f"parkcode: {row['api_call.parkCode']}"}
    return dict

def save_to_jsonl(dataframe, filename,target):
    """
    Writes record to json with correct GPT format
    """
    with open(filename, 'w') as f:
        for _, row in dataframe.iterrows():
            example = create_prompt_response(row,target)
            json.dump(example, f)
            f.write('\n')


def handle_query(query, model, client, max_tokens):
    prompt = f"prompt: {query}\n"
    response = client.completions.create(
        model=model,  
        prompt=prompt,
        max_tokens=max_tokens
    )
    completion = response.choices[0].text#.strip()
    return completion