#!/usr/bin/env python3
"""Generate forms for human evaluation."""

from jinja2 import FileSystemLoader, Environment
import os
import glob
import numpy as np


def main():
    """Main function."""
    loader = FileSystemLoader(searchpath="./templates")
    env = Environment(loader=loader)
    template = env.get_template("mos.html.jinja2")

    model_a_wav_paths = sorted(glob.glob("wavs/model_a/*/raw*.wav"), key=lambda x: int(x.split(os.sep)[-1].split("_")[-1].split(".")[0]))
    model_b_wav_paths = sorted(glob.glob("wavs/model_b/*/*.flac"), key=lambda x: int(x.split(os.sep)[-1].split("_")[-1].split(".")[0]))
    model_c_wav_paths = sorted(glob.glob("wavs/model_c/*/*.wav"), key=lambda x: int(x.split(os.sep)[-1].split("_")[-1].split(".")[0]))
    model_a_wav_paths = sorted(glob.glob("wavs/model_a/*/raw*.wav"), key=lambda x: int(x.split(os.sep)[-1].split("_")[-1].split(".")[0]))
    assert len(model_a_wav_paths) == len(model_b_wav_paths)
    assert len(model_a_wav_paths) == len(model_c_wav_paths)

    # check that the ordering matches for all lists and all files in them
    for _n in range(len(model_a_wav_paths)):
        num_a = model_a_wav_paths[_n].split(os.sep)[-1].split("_")[-1].split(".")[0]
        num_b = model_b_wav_paths[_n].split(os.sep)[-1].split("_")[-1].split(".")[0]
        num_c = model_c_wav_paths[_n].split(os.sep)[-1].split("_")[-1].split(".")[0]
        assert int(num_a) > -1
        assert num_a != ""
        assert num_a == num_b
        assert num_a == num_c

    base_seed = 4142
    random_state = np.random.RandomState(base_seed)

    # the file sets we use later for hiding/unhiding question groups
    file_sets = []
    seq = np.arange(len(model_a_wav_paths))
    jump = 4
    keep = 7
    for _i in range(len(seq)):
        if _i % jump == 0:
            _li = seq[_i:_i + keep]
            if len(_li) < keep:
                break
            files_a = [model_a_wav_paths[_el] for _el in _li]
            files_b = [model_b_wav_paths[_el] for _el in _li]
            files_c = [model_c_wav_paths[_el] for _el in _li]
            file_sets.append(([_l for _l in _li], files_a, files_b, files_c))

    combined = []
    combined.extend(model_a_wav_paths)
    combined.extend(model_b_wav_paths)
    combined.extend(model_c_wav_paths)
    remapping = {}
    inds = list(range(len(combined)))
    inds2 = list(range(len(combined)))
    random_state.shuffle(inds2)
    for _i, _c in enumerate(combined):
        remapping[_c] = (inds[_i], inds2[_i])
    rev_remapping = {v[1]: (v[0], k) for k, v in remapping.items()}

    # use final_list for all sites
    # just choose which sets to hide based on randomness
    final_list = [None for _ in range(len(combined))]
    for _i, _c in enumerate(combined):
        final_list[remapping[_c][1]] = _c

    # check that we can unshuffle them...
    recombined = [None for _ in range(len(final_list))]
    for _i, _c in enumerate(final_list):
        recombined[remapping[final_list[_i]][0]] = _c
    assert combined == recombined

    """
    questions_list = [
            {
                "title": "file 1",
                "audio_path": "wavs/test1.wav",
                "name": "q1"
            },
            {
                "title": "file 2",
                "audio_path": "wavs/test2.wav",
                "name": "q2"
            },
    ]
    """
    # use file_sets to determine what to hide and what to show
    selected_file_set = file_sets[0]

    # file set 0 is webpage 1
    all_selected_files = {}
    for _el in selected_file_set[1] + selected_file_set[2] + selected_file_set[3]:
        all_selected_files[_el] = True

    questions_list = []
    true_so_far = 0
    for _n, _f in enumerate(final_list):
        entry = {}
        if _f in all_selected_files:
            true_so_far += 1
            entry["style"] = "display: block;"
            entry["title"] = "Question {}".format(true_so_far)
        else:
            entry["style"] = "display: none;"
            entry["title"] = "hidden"
        entry["audio_path"] = _f
        entry["name"] = "q" + str(_n)
        questions_list.append(entry)

    html = template.render(
        page_title="LISTENING TEST",
        form_url="https://script.google.com/macros/s/AKfycbyJLPpkQMvCPb2KBa9tGaEdNtwJzCLROA27GEUbgEHO2HRKeDoOTlnJkrSQin3LfK2qsQ/exec",
        form_id=1,
        questions=questions_list,
    )
    print(html)


if __name__ == "__main__":
    main()
