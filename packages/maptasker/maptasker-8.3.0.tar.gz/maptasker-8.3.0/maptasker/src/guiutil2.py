#! /usr/bin/env python3
"""

 guiutil2: General and GUI utilities.

These are functions pulled out of maputils, guiwins and guiutils that would otherwise cause a circular
import error.

"""

import os
import platform
import re
import tkinter as tk
import tkinter.font as tkfont
from io import BytesIO

import customtkinter as ctk
import requests
from PIL import Image, ImageTk

from maptasker.src.aiutils import get_api_key
from maptasker.src.error import rutroh_error
from maptasker.src.primitem import PrimeItems

# Define label fonts for headings: 0=h0, 1=h1, etc.
heading_fonts = {"0": 12, "1": 18, "2": 17, "3": 16, "4": 15, "5": 14, "6": 13}


def validate_tkinter_geometry(geometry_string: str) -> bool:
    """
    Validates a tkinter window geometry string with additional constraints.

    Args:
        geometry_string (str): The geometry string in the format
                                 'width x height + position_x + position_y'.

    Returns:
        bool: True if the geometry string is valid and meets the constraints,
              False otherwise.
    """
    pattern = re.compile(r"^\d+x\d+\+\d+\+\d+$")
    if not pattern.match(geometry_string):
        return False

    try:
        parts = geometry_string.replace("+", " ").replace("x", " ").split()
        width = int(parts[0])
        height = int(parts[1])
        pos_x = int(parts[2])
        pos_y = int(parts[3])

        if width < 300:
            print("Error: Window width must be at least 300.")
            return False
        if height < 50:
            print("Error: Window height must be at least 50.")
            return False
        if pos_x < 0:
            print("Error: Window position X must be a non-negative number.")
            return False
        if pos_y < 0:
            print("Error: Window position Y must be a non-negative number.")
            return False

        return True  # noqa: TRY300
    except ValueError:
        print("Error: Invalid numeric value in geometry string.")
        return False


def configure_progress_bar(output_lines: list, title: str) -> tuple:
    """
    Configures and returns a progress bar for the GUI if the 'gui' argument is set in PrimeItems.program_arguments.

    Args:
        output_lines (list): The list of lines to process.
        titele (str): The title of the progress bar.

    Returns:
        progress (dict): The progress bar dictionary.
    """
    # Display a progress bar if coming from the GUI.
    if PrimeItems.program_arguments["gui"]:
        # Avoid a circular import error.  It's gotta be here.
        from maptasker.src.guiwins import ProgressbarWindow  # noqa: PLC0415

        # Make sure we have a geometry set for the progress bar
        if not PrimeItems.program_arguments["map_window_position"]:
            PrimeItems.program_arguments["map_window_position"] = "300x200+600+0"
        # Create a progress bar widget
        # The progress_bar will point to the ProgressbarWindow object, and progress_bar.progressbar will point to the
        # CTkProgressBar object
        progress_bar = ProgressbarWindow()
        progress_bar.title(f"{title} Progress")
        progress_bar.progressbar.set(0.0)
        progress_bar.progressbar.start()
        progress_bar.progressbar.focus_set()

        # Set the geometry of the progress bar
        if validate_tkinter_geometry(
            PrimeItems.program_arguments["progressbar_window_position"],
        ):
            progress_bar.geometry(
                PrimeItems.program_arguments["progressbar_window_position"],
            )

        else:
            PrimeItems.program_arguments["progressbar_window_position"] = "300x500+100+0"
        # Setup for our progress bar.  Use the total number of output lines as the metric.
        # 4 times since we go thru output lines 4 times in a majore way...
        # 1st: the Diagram, 2nd: delete_hanging_bars
        max_data = len(output_lines) * 8

        # Calculate the increment value for each 10% of progress (tenth_increment) based on the maximum value of the
        # progress bar (max_data). If the calculated increment is 0 (which would happen if max_data is less than 10),
        # it sets the increment to 1 to avoid division by zero issues.
        tenth_increment = max_data // 10
        if tenth_increment == 0:
            tenth_increment = 1

        # Save the info
        PrimeItems.progressbar = {
            "progress_bar": progress_bar,
            "tenth_increment": tenth_increment,
            "max_data": max_data,
            "progress_counter": 0,
            "self": None,
        }

        return PrimeItems.progressbar

    # Not the GUI.  Just return an almost empty dictionary.
    return {
        "progress_counter": 0,
    }


# Define the output file for the trace log
TRACE_LOG_FILE = "trace_log.txt"

# Function to clear the log file at the start (optional)
if os.path.exists(TRACE_LOG_FILE):
    os.remove(TRACE_LOG_FILE)


def my_trace_function(frame, event, arg) -> None:  # noqa: ANN001
    """
    Custom trace function that logs execution details.

    Invoked with:
    import sys
    from maptasker.src.guiutil2 import my_trace_function
    if PrimeItems.program_arguments["debug"]:
            PrimeItems.trace = True
            sys.settrace(my_trace_function)
    """
    # Only start logging if the 'start_tracing' flag is True
    if not PrimeItems.trace:
        return my_trace_function  # Keep the trace function active but don't log yet

    # Get relevant information from the frame
    co = frame.f_code
    filename = co.co_filename
    lineno = frame.f_lineno
    func_name = co.co_name

    # --- ADD THIS CHECK ---
    # Skip if the filename is not a regular file path (e.g., frozen modules, <string>, etc.)
    # Or if it refers to the trace function itself to avoid recursion
    if (
        not os.path.exists(filename)
        or not os.path.isfile(filename)
        or func_name == "my_trace_function"
        or filename == os.path.basename(__file__)
        or "<frozen" in filename
    ):  # Explicitly check for frozen modules
        return my_trace_function
    # --- END ADDITION ---

    log_message = ""
    if event == "line":
        # Get the line of code being executed
        try:
            with open(
                filename,
                encoding="utf-8",
            ) as f:  # Use the full filename here
                lines = f.readlines()
                current_line_code = lines[lineno - 1].strip() if 0 <= lineno - 1 < len(lines) else "<CODE NOT FOUND>"
        except (OSError, UnicodeDecodeError) as e:
            # Handle potential file access or decoding errors gracefully if they slip past the initial check
            current_line_code = f"<ERROR READING CODE: {e}>"
            # You might want to log this error to a separate debug log
            # print(f"Warning: Could not read source for {filename}:{lineno} - {e}", file=sys.stderr)

        log_message = f"LINE: {os.path.basename(filename)}:{lineno} {func_name}() - {current_line_code}"
    elif event == "call":
        log_message = f"CALL: {os.path.basename(filename)}:{lineno} Entering function: {func_name}()"
    elif event == "return":
        log_message = f"RETURN: {os.path.basename(filename)}:{lineno} Exiting function: {func_name}() (Returned: {arg})"
    elif event == "exception":
        exc_type, exc_value, _ = arg
        log_message = (
            f"EXCEPTION: {os.path.basename(filename)}:{lineno} {func_name}() - {exc_type.__name__}: {exc_value}"
        )

    if log_message:
        with open(TRACE_LOG_FILE, "a") as f:
            f.write(log_message + "\n")

    # Important: The trace function must return itself (or another trace function)
    # to continue tracing in the current or new scope.
    return my_trace_function


def is_valid_ai_config(self: ctk) -> bool:
    """
    Validates the AI model and API key against predefined configurations in PrimeItems.

    This method iterates through a list of known AI providers (e.g., OpenAI, Anthropic, Gemini)
    and checks if the instance's `self.ai_model` exists within any provider's model list.
    If a matching model is found, it further checks if the `self.ai_apikey` matches
    the corresponding API key stored in `PrimeItems.ai` for that provider.
    Some providers (like 'llama' in this example) may not require an API key check.

    The method prints a message indicating whether the AI model and API key combination
    is considered valid based on the configurations.

    Returns:
        bool: True if the `self.ai_model` and `self.ai_apikey` (if required)
              are valid according to `PrimeItems.ai` configurations; False otherwise.
    """
    # Dictionary mapping provider names to their models and key attributes in PrimeItems.ai
    # If 'llama_models' needs an API key, add 'llama_key' here.
    ai_providers = {
        "openai": {"models": "openai_models", "key": "openai_key"},
        "anthropic": {"models": "anthropic_models", "key": "anthropic_key"},
        "gemini": {"models": "gemini_models", "key": "gemini_key"},
        "deepseek": {"models": "deepseek_models", "key": "deepseek_key"},
        "llama": {"models": "llama_models", "key": None},  # Assuming no key for llama based on original if
    }
    if not self.ai_model:
        return False  # Don't do anything if there is no model to check against.

    # Make sure we have read in the api keys.
    if not self.ai_apikey or self.ai_apikey == "Hidden":
        self.ai_apikey = get_api_key()

    is_valid_config = False
    for provider, config in ai_providers.items():
        models = PrimeItems.ai.get(config["models"], [])
        key_to_check = PrimeItems.ai.get(config["key"], None)
        api_key = key_to_check if provider != "llama" and key_to_check == PrimeItems.ai[f"{provider}_key"] else None

        # If llama, then we need to strip " (Installed)" off the name.
        if provider == "llama":
            models = [item.replace(" (installed)", "") for item in models]

        if self.ai_model in models:
            if provider != "llama" and not api_key:
                # We have found the model but it doesn't have the api key.
                break
            if api_key is None or PrimeItems.ai[config["key"]] == api_key:  # No key check needed for this provider
                is_valid_config = True
                self.ai_apikey = api_key
                break
            break

    return is_valid_config


def get_changelog_file(url: str, delimiter: str, n: int) -> list:
    """
    Fetches a text file from a URL and returns a list of lines until the nth
    occurrence of a specified delimiter is encountered.

    Args:
        url (str): The URL of the text file.
        delimiter (str): The string to count occurrences of (e.g., "##").
        n (int): The nth occurrence of the delimiter to stop at.

    Returns:
        list: A list of text lines up to (but not including) the line
              where the nth occurrence of the delimiter is found.
              Returns an empty list if the URL is invalid or the delimiter
              is not found 'n' times.
    """
    if n <= 0:
        rutroh_error(f"Invalid integer value for n: {n!s}")
        return []

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
    except requests.exceptions.RequestException as e:
        rutroh_error(f"Error fetching the URL: {e}")
        return []

    lines = []
    delimiter_count = 0

    # Decode the content and split into lines
    text_content = response.text
    for line in text_content.splitlines():
        if line.startswith(f"{delimiter} "):
            delimiter_count += 1
        if delimiter_count == n:
            break  # Stop when the nth occurrence is found
        lines.append(line)

    return lines


def draw_box_around_text(self: ctk, line_num: int) -> tuple[int, list]:
    """Draws a box around text in a custom textbox widget.

    This function iterates through a set of text values, formats them,
    and inserts them into a textbox widget. It configures a tag for each
    piece of text to apply a specific font, foreground color, and background color,
    effectively creating a styled "box" around the text.

    Args:
        self: The instance of the custom textbox class (ctk).
        line_num: The starting line number where the text will be inserted.

    Returns:
        The final line number.
    """
    mygui = self.master.master
    all_values = self.draw_box["all_values"]
    line_num_str = str(line_num)
    begin_box = f"{line_num_str}.0"
    max_msg_len = 0
    number_of_inserted_lines = 0
    end_of_label = False
    prev_msg = "---none---"
    its_a_label = True
    first_message = True
    self.previous_heading = "0"
    self.previous_font = "None"

    # Get the background color
    bg_color = make_hex_color(mygui.color_lookup["background_color"])

    # Outerloop on all_valuies for all lines in label
    # Innerloop for values of label on the same line.
    # Microloop for all newline-deliminated messages on same line.

    # Outerloop on all_valuies for all lines in label
    # Go through all of the values in the label and output them
    for num, value in enumerate(all_values):
        # value is a dictionary of lists for 'text', 'color', etc."high"
        # Get spacing only if this is first element.
        if num == 0:
            spacing = value["spacing"]
            spacer_newline = value["spacing"]
        char_position = 0

        # Innerloop for values of label on the same line.
        # Iterate over a list or a string.
        for inner_num, message in enumerate(value["text"]):
            # Set our end of label if this is the end.
            if value["end"][inner_num]:
                end_of_label = True

            # clean_message = message.replace("\n\n", "\n")
            clean_message = message
            if clean_message == "<p>":
                clean_message = "\n"

            # Build the start end indecies
            start_idx = str(line_num) + "." + str(char_position)

            # Handle a single, new line.
            if clean_message == "\n" or not clean_message:
                char_position, spacing, line_num, start_idx = _insert_newline(self, start_idx, value, line_num)

                # Keep track of the maximum message length
                max_msg_len = _get_max_msg_len(clean_message, max_msg_len)
                continue

            # The message can have embedded newlines...handle them.
            # Break message up by newline
            all_messages = clean_message.split("\n")

            # Microloop for all newline-deliminated messages on same line.
            # Iterate through all messages per line
            for msg_num, msg in enumerate(all_messages):
                # if "===============" in msg:
                #     print("bingo", value["table"][inner_num])
                # Handle images separetaly
                if "<img src=" in msg:
                    _handle_image(self, msg, start_idx)
                    continue

                # Ignore paragraphs
                if msg in ("<p>", "</a>"):
                    continue

                # Determine if this is a label vs TaskerNet description
                if "TaskerNet description:" in msg:
                    its_a_label = False
                    new_msg = msg.replace("TaskerNet description:", "TaskerNet description:\n")
                else:
                    new_msg = msg

                new_msg = "" if new_msg == "<p>" else new_msg

                # If Taskernet Description, alter the color so it isn't task_label_color
                if not its_a_label and value["color"][inner_num] == PrimeItems.colors_to_use["action_label_color"]:
                    value["color"][inner_num] = PrimeItems.colors_to_use["taskernet_color"]

                # Bailout if we hit our end-of-label flag.
                if not end_of_label and (value["end"][inner_num] or ":lblend" in new_msg):
                    end_of_label = True
                    # Get rid of end-of-label flag and add a space at end of last line.
                    updated_msg = new_msg.replace('<data-flag=":lblend">', "") + " "
                elif end_of_label:
                    updated_msg = new_msg.replace('<data-flag=":lblend">', "")
                else:
                    updated_msg = new_msg

                # Handle a blank message, but don't output consequtive blank lines.
                if updated_msg == "":
                    if prev_msg != "":
                        char_position, spacing, line_num, start_idx = _insert_newline(self, start_idx, value, line_num)
                        prev_msg = ""
                    continue

                # Set the spacing after the line
                between_line_spacing = -20 if updated_msg.startswith("   *") else 0

                # Readjust the message by adding a blank at the end so it doesn't bump up against box.
                msg_to_insert = updated_msg.replace("&nbsp;", " ").replace("<p>", "\n").replace("</p></div>", "")

                # Add a blank to the front if this is and TaskerNet description and the start of a line
                if (
                    char_position == 0
                    and not its_a_label
                    and not msg_to_insert.startswith(" ")
                    and not msg_to_insert.startswith("<a href=")
                ):
                    msg_to_insert = " " + msg_to_insert

                # Insert and tag the message
                max_msg_len, char_position = _insert_and_tag(
                    self,
                    msg_to_insert,
                    max_msg_len,
                    spacing,
                    between_line_spacing,
                    start_idx,
                    char_position,
                    bg_color,
                    value,
                    inner_num,
                )
                number_of_inserted_lines += 1

                # If this is the very first message, set the beginning of the bounding box based on the textbox content.
                # Loop through the lines starting at the last and working backwards,
                # looking for the first line that doesn't contain our message.
                if first_message:
                    first_message = False

                    # Get the line and column index of the last character in the Text widget.
                    # The 'end-1c' index is a special index that represents the character just
                    # before the absolute end of the widget's content.
                    last_char_index = self.textview_textbox.index(tk.END + "-1c")
                    line_number, _ = last_char_index.split(".")

                    # Find and set the beginning of the bounding box to the first line.
                    prev_num = int(line_number)
                    content = ""
                    if "\n" in msg_to_insert:
                        msg_to_insert = msg_to_insert.split("\n")[1]  # Skip 'TaskerNet description:'
                    while msg_to_insert not in content:
                        content = self.textview_textbox.get(f"{prev_num!s}.0", f"{prev_num!s}.end")
                        if msg_to_insert not in content:
                            prev_num -= 1
                    begin_box = f"{prev_num}.0" if its_a_label else f"{prev_num - 1}.0"
                    line_num = int(line_number)

                # Reset spacing so we don't get spacers every concatenated piece of text.
                spacing = 0

                # Bump everything if we are doing a multiline message and we are not at the end.
                if len(all_messages) > 1 and msg_num < len(all_messages) - 1:
                    char_position = 0
                    line_num += 1
                    start_idx = str(line_num) + ".0"
                    spacing = spacer_newline

                # Save our previous msg to avoid too many blank lines.
                prev_msg = msg_to_insert

            # Bailout if end of the label
            if end_of_label:
                break

        # Bailout if end of the label.  Add one blank to end of box to force a full-line width on the box.
        if end_of_label:
            if prev_msg != "":
                line_num += 1
                char_position, spacing, line_num, start_idx = _insert_newline(self, f"{line_num!s}.0", value, line_num)
            break

        char_position = 0

    # Add a final newline to even out the bottom of the box if there is text at the bottom if thjis is not a one-liner.
    if number_of_inserted_lines > 0:
        content, _ = get_last_line(self.textview_textbox, start_idx)
        if content:
            line_num += 1
            start_idx = str(line_num) + ".0"
            self.textview_textbox.insert(start_idx, "\n")
        # If the last line is blank, delete it.
        else:
            self.textview_textbox.delete(start_idx)
            line_num -= 1
            start_idx = str(line_num) + ".0"

    # Add the bounding box as a highlight by adding a highlighted tag
    bbox_tag = f"{begin_box}:bbox"
    # Bump the box ahead one line if this is a TaskerNet description.  We don't want to enclose that string.
    if not its_a_label:
        begin_box = f"{(int(begin_box.split('.')[0]) + 1)!s}.0"
    end_box = f"{line_num!s}.{max_msg_len + 1!s}"
    self.textview_textbox.tag_add(bbox_tag, begin_box, end_box)
    self.textview_textbox.tag_config(
        bbox_tag,
        background=bg_color,
        relief="ridge",
        borderwidth=2,
        spacing1=5,
        spacing2=-30,
        spacing3=5,
        rmargin=10,
    )

    # Point to the next available line by geting our last line number.
    # line_num = begin_box.split(".")[0]
    line_num = int(line_num) + 1

    # Insert a newline after the label
    self.textview_textbox.insert(f"{line_num}.0", "\n", "bg_color")
    line_num += 1

    # Configure the tag for the background color
    self.textview_textbox.tag_config(
        "bg_color",
        background=bg_color,
    )

    # Reset draw_box for next label
    self.draw_box = {"all_values": [], "start_idx": None, "end_idx": None, "spacing": 0, "end": False}

    return line_num


def _insert_and_tag(
    self: ctk,
    message: str,
    max_msg_len: int,
    spacing: int,
    between_line_spacing: int,
    start_idx: str,
    char_position: int,
    bg_color: str,
    value: dict,
    inner_num: int,
) -> tuple[int, int, int]:
    """Inserts and tags a message in a custom text widget.

    This private helper function is responsible for inserting a formatted message
    into a text widget (`textview_textbox`), applying a custom tag to it, and
    configuring the tag with specific font, background, and foreground colors.
    It also updates various tracking variables like line number and character position.

    Parameters
    ----------
    self : ctk
        The instance of the `ctk` class, which holds the text widget.
    message : str
        The string content to be inserted into the text widget.
    max_msg_len : int
        The current maximum length of a message. This value is updated if the
        current message is longer.
    spacing : int
        The number of leading spaces to add to the message. A value of 0 means
        no leading spaces are added.
    between_line_spacing : int
        The spacing to add after the current line ('spacing2' in tag_config)
    start_idx : str
        The starting index (e.g., "1.0") for the text insertion.
    char_position : int
        The character position on the current line.
    bg_color : str
        The background color for the text, specified as a string.
    value : dict
        A dictionary containing formatting information, including 'spacing',
        'highlights', and 'color'.
    inner_num : int
        An index used to access specific values from the 'highlights' and
        'color' lists within the `value` dictionary.

    Returns
    -------
    tuple[int, int, int]
        A tuple containing the updated values for:
        - `max_msg_len`
        - `char_position`
    """
    mygui = self.master.master
    # Get the highlight/font attribute for this specific message.
    highlights = value["highlights"][inner_num]

    # Get the font(s), if any.
    temp_font = highlights.split(";")

    # Get the font size / italic flag / bold
    heading_num = self.previous_heading
    if temp_font[0] == "italic":
        font = "italic"
    elif temp_font[0] == "bold":
        font = "bold"
    else:
        # Highlight is a heading rather than a font specification.
        heading_num = "0" if message == " TaskerNet description:\n " else temp_font[0].replace("-text", "")[1]
        font = "normal"

    # Handle underlining: True or False
    underline = value["decor"][inner_num] == "underline"

    # Set the font size to the heading size.  If this is a list item, downsize it.
    try:
        font_size = heading_fonts[heading_num]
    except KeyError:
        font_size = heading_fonts["0"]  # Default to h0 if not found
    if platform.system() == "Windows":  # Font sizes are different on windows.
        font_size = font_size * 2

    if PrimeItems.program_arguments["debug"] and not message.startswith("<a href="):
        message = f"{font_size}{message}"

    # Reduce spacing if this is the largest font
    font_sizes = list(heading_fonts.values())
    max_font_size = max(font_sizes)
    if font_size == max_font_size:
        spacing = spacing // 2 if spacing > 0 else 0

    # Assign the font to use: define the font if we don't yet have it.
    # font_to_use = assign_font(self, mygui.font, font_size, font, underline)
    font_key = mygui.font + font + str(font_size)
    try:
        font_to_use = mygui.font_table[font_key]
    except KeyError:
        font_to_use = assign_font(self, mygui.font, font_size, font, underline)
        mygui.font_table[font_key] = font_to_use

    # Handle hotlink 'href'
    if "<a href=" in message:
        temp = message.split('"')
        href = temp[1]
        text_len = len(temp[2]) - 4
        message = temp[2][1:text_len]
        # Add the link
        tag_id = self.textview_hyperlink.add(href)
        self.textview_textbox.insert(
            start_idx,
            message,
            tag_id,
        )
    else:
        href = ""
        # Create a tag with the text attributes
        tag_id = f"{heading_num};{font}:{value['color'][inner_num]}:{value['decor'][inner_num].strip()}:{between_line_spacing}"

    # Format the message
    spacer = " " * spacing
    formatted_message = spacer + message if spacing > 0 else message

    # Keep track of largest message
    max_msg_len = _get_max_msg_len(formatted_message, max_msg_len)

    # Get the html attributes
    fg_color = make_hex_color(value["color"][inner_num])

    # Insert the unformatted text...only if it is normal text and not a hotlink
    if not href:
        # Apply the html attributes
        _configure_tag(self, tag_id, font_to_use, bg_color, fg_color, underline, between_line_spacing)

        # Do the second font, if there is one.
        if len(temp_font) > 1:
            new_font = temp_font[1]
            tag_id = tag_id.replace(font, new_font)
            font_to_use = (mygui.font, font_size, new_font)
            # Apply the html attributes
            _configure_tag(self, tag_id, font_to_use, bg_color, fg_color, underline, between_line_spacing)

        # Specifying the tag_id in the insert eliminates the need to do a tag_add.
        self.textview_textbox.insert(start_idx, formatted_message, tag_id)

    char_position += len(formatted_message)
    self.previous_heading = heading_num
    self.previous_font = font_to_use
    self.previous_between_line_spaccing = between_line_spacing

    return max_msg_len, char_position


def _configure_tag(
    self: ctk,
    tag_id: str,
    font_to_use: tkfont,
    bg_color: str,
    fg_color: str,
    underline: str,
    between_line_spacing: int,
) -> None:
    self.textview_textbox.tag_config(
        tag_id,
        font=font_to_use,
        background=bg_color,
        foreground=fg_color,
        underline=underline,
        spacing2=between_line_spacing,
    )


def assign_font(self, font_name: str, font_size: int, font: str, underline: bool) -> tkfont:
    """Creates and returns a CTkFont object with specified attributes.

    This function generates a CustomTkinter font object based on a given font family,
    size, and style. It supports "normal", "bold", and "italic" styles.

    Args:
        self (ctk): The CustomTkinter object instance.
        font_name (str): The name of the font family (e.g., "Arial").
        font_size (int): The size of the font in points.
        font (str): The font style. Must be one of "normal", "bold", or "italic".
        underline (bool): A boolean indicating whether the font should be underlined.

    Returns:
        tkfont: A configured CTkFont object.

    Raises:
        ValueError: If an unsupported font style is provided.
    """
    if font == "normal":
        return ctk.CTkFont(family=font_name, size=font_size, underline=underline)
    if font == "bold":
        return ctk.CTkFont(family=font_name, size=font_size, weight="bold", underline=underline)
    return ctk.CTkFont(family=font_name, size=font_size, slant="italic", underline=underline)


def _handle_image(self: ctk, msg: str, start_idx: str) -> None:
    """
    Extracts an image URL from an HTML 'href' attribute and displays the image.

    This function searches for a URL embedded within an 'href' attribute
    in the provided message string. If a URL is found, it calls a helper
    function to display the image in a CustomTkinter text view widget.
    If no URL is found, it prints an error message to the console.

    Args:
        self (ctk): The CustomTkinter object instance, which contains the
                    text view widget.
        msg (str): The string message containing the HTML-like 'href' attribute.
        start_idx (str): The starting index for the image display in the
                         text view widget (e.g., "end").
    """
    # Get the url for the image
    # This pattern looks for "href=" followed by a quote, then captures everything
    # that's not a quote, until it finds the closing quote.
    # (?:...) is a non-capturing group.
    # (.*?) is a non-greedy match for any character.
    pattern = r'href="(.*?)"'
    # Search for the pattern in the string

    match = re.search(pattern, msg)

    # Check if a match was found
    if match:
        # The URL is in the first captured group (index 1)
        url = match.group(1)
        _show_image(self.textview_textbox, url, start_idx)
    else:
        rutroh_error("No URL found in the href attribute.")


def _show_image(text_widget: ctk.CTkTextbox, image_url: str, index: str) -> None:
    """
    Downloads an image from a URL and displays it in a CTkTextbox widget.

    Args:
        text_widget: The customtkinter CTkTextbox widget instance.
        image_url: The URL of the image to display.
        index: The text index where the image should be inserted.
    """
    try:
        # 1. Download the image
        response = requests.get(image_url, timeout=5, headers={"User-agent": "your bot 0.1"})
        if response.status_code == 429:
            text_widget.insert(index, "[!!! Image server too many requests !!!]", "error")
            return

        response.raise_for_status()

        # 2. Open the image using Pillow.
        img_data = BytesIO(response.content)
        # pil_image = Image.open(img_data).resize((300, 300), Image.LANCZOS)
        pil_image = Image.open(img_data)

        # 3. Use thumbnail() to resize while preserving the aspect ratio.
        # This will resize the image to fit within a 300x200 box without distortion.
        pil_image.thumbnail((300, 200), Image.LANCZOS)

        # 4. Create a standard Tkinter PhotoImage from the Pillow image.
        # This is necessary for the internal Tkinter Text widget.
        tk_image = ImageTk.PhotoImage(pil_image)

        # 5. Embed the image in the internal Tkinter Text widget.
        # This is the key fix: use the `_textbox` attribute, which is a 'tk' rather than a 'ctk' reference.
        text_widget._textbox.image_create(index, image=tk_image)  # noqa: SLF001

        # 6. Store a reference to prevent garbage collection.
        # The image reference must be a property of the main widget or a global variable.
        if not hasattr(text_widget, "image_references"):
            text_widget.image_references = []
        text_widget.image_references.append(tk_image)

    except requests.exceptions.RequestException as e:
        rutroh_error(f"Failed to download image: {e}")
    except Exception as e:  # noqa: BLE001
        rutroh_error(f"guiutil2 _show_image...An error occurred: {e}")


def _insert_newline(self: ctk, start_idx: str, value: dict, line_num: int) -> tuple[int, int, int, str]:
    """Inserts a newline character into the textbox and updates state variables.

    This helper function is designed to handle the logic for adding a new line
    to the Tkinter text widget, resetting the character position, and
    incrementing the line number for subsequent text insertions.

    Args:
        self: The instance of the custom textbox class (ctk).
        start_idx: The current starting index for text insertion.
        value: A dictionary containing data, including spacing information.
        line_num: The current line number.

    Returns:
        A tuple containing:
        - The reset character position (always 0).
        - The spacing value for the new line.
        - The updated line number.
        - The new start index string.
    """
    self.textview_textbox.insert(start_idx, "\n")
    char_position = 0
    line_num += 1
    start_idx = str(line_num) + "." + str(char_position)
    return 0, value["spacing"], line_num, start_idx


def _get_max_msg_len(message: str, max_msg_len: int) -> int:
    """Get the maximum length of the messages"""
    return max(max_msg_len, len(message))


def make_hex_color(color: str) -> str:
    """
    Converts a given color string to a hex color string if it's a digit.

    Args:
        color (str): The color string to be converted.

    Returns:
        str: The hex color string if the input is a digit, otherwise the original color string.
    """
    # Add color to the tag
    if color.isdigit():
        return "#" + color
    return color


def get_last_line(text_widget: ctk.CTkTextbox, start_idx: str) -> tuple[str, str]:
    """Gets the content and index of the last line of a text widget.

    This function retrieves the text of the last line in a CTkTextbox widget,
    excluding the final newline character. It also returns the starting index
    of that line, which is useful for subsequent operations like deletion or
    replacement.

    Parameters
    ----------
    text_widget : ctk.CTkTextbox
        The custom Tkinter textbox widget from which to retrieve the text.
    start_idx : str
        The starting index of the last line.


    Returns
    -------
    tuple[str, str]
        A tuple containing two strings:
        - The content of the last line.
        - The starting index of the last line (e.g., "5.0").

    Raises
    ------
    TclError
        If the text widget is empty, a TclError is raised and handled by
        calling the `rutroh_error` function.
    """
    try:
        # Start at bottom of textbox and work backwards until we have some content
        dont_have_info = True
        last_line_index = start_idx
        while dont_have_info:
            line_to_get = str(int(last_line_index.split(".")[0]) - 1) + ".0"
            content = text_widget.get(line_to_get, "end-1c")
            return content.replace("\n", ""), line_to_get

        # # Print the result
        # print(f"The last line of text is: '{last_line_content}'")

    except tk.TclError:
        rutroh_error("The text widget is empty.")
