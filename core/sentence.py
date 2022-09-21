import re
from setup.settings import preprocessing


# Load answer replaces
with open(preprocessing['answers_replace_file'], 'r', encoding='utf-8') as answers_replace_file:
    answers_replace = list(filter(lambda word: False if word[0] == '#' else True, filter(None, answers_replace_file.read().split("\n"))))

# Replaces phrases in answers
def replace_in_answers(answers):

    replaces_answers = []

    # For every answer
    for answer in answers:

        # And every regex rule
        for replace in answers_replace:

            difference = 0
            replace = replace.split('##->##')
            replace_from = replace[0].strip()
            replace_to = replace[1].strip()

            # If replace regex was found in answer
            if re.search(replace_from, answer):

                # Search for all occurrences and iterate thru them again
                regex = re.compile(replace_from)
                for p in regex.finditer(answer):

                    # Calculate data
                    replace_from = p.groups()[0]
                    replace_to = re.sub(r'\\(\d+)', lambda x: p.groups()[int(x.groups()[0])], replace_to)
                    position = p.start(1) + difference
                    difference += -len(replace_from) + len(replace_to)

                    # Remove spaces
                    answer = answer[:position] + answer[position:].replace(replace_from, replace_to, 1)

        replaces_answers.append(answer)

    return replaces_answers

# Normalize newlines
def normalize_new_lines(answers):

    # Replace 'newlinechar' by '\n' and multiple newlines with one
    answers = [re.sub('[ \n]*newlinechar([ \n]|$)+', '\n', answer) for answer in answers]
    return [re.sub('\n+', '\n', answer).strip() for answer in answers]



# Score response
def score_answers(question, answers):

    # Scoring enabled?
    if not score_settings['use_scoring']:
        return {'score': list(reversed(range(-len(answers) + 1, 1))), 'score_modifiers': [] * len(answers)}

    # Functions to run
    functions = [
        check_urls,
        ending,
        ascii_emoticons,
        unk,
        subsentence_score,
        position,
        reward_longer_sentences,
        question_answer_similarity_by_ratio,
        #question_answer_diffrence_by_distance,
        answer_subsentence_similarity_by_ratio,
        #answer_subsentence_diffrence_by_distance,
    ]

    scores = {'score': [], 'score_modifiers': []}

    # Iterate thru answers, apply every scoring function
    for i, answer in enumerate(answers):

        score_modifiers = [function(i+1, question, answer) for function in functions]
        scores['score'].append(score_settings['starting_score'] + sum(score_modifiers))
        scores['score_modifiers'].append(score_modifiers)

    # Return score
    return scores
