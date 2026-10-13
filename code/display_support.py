import ctypes
import os


BASE_DPI = 96

RESOLUTION_DIMENSIONS = {
    '0': (1366, 768),
    '1': (1440, 900),
    '2': (1680, 1050),
    '3': (1920, 1080),
    '4': (1920, 1200),
    '5': (2560, 1440),
    '6': (3440, 1440),
    '7': (3840, 2160),
    '8': (5120, 2880),
}

MAP_CAPTURE_PROFILES = {
    '0': (1034, 436, 329, 329, 329, 329),
    '1': (1054, 514, 384, 384, 384, 384),
    '2': (1234, 604, 444, 444, 444, 444),
    '3': (1462, 622, 456, 456, 456, 456),
    '4': (1462, 742, 456, 456, 456, 456),
    '5': (1955, 835, 605, 605, 465, 605),
    '6': (2835, 835, 605, 605, 465, 605),
    '7': (2940, 1260, 900, 900, 480, 900),
    '8': (3924, 1684, 1196, 1196, 460, 1196),
}


def enable_process_dpi_awareness():
    if os.name != 'nt':
        return 'unsupported'

    user32 = ctypes.WinDLL('user32', use_last_error=True)
    set_context = getattr(user32, 'SetProcessDpiAwarenessContext', None)
    if set_context is not None:
        set_context.argtypes = [ctypes.c_void_p]
        set_context.restype = ctypes.c_bool
        if set_context(ctypes.c_void_p(-4)):
            return 'per-monitor-v2'
        if ctypes.get_last_error() == 5:
            return 'already-configured'

    try:
        shcore = ctypes.WinDLL('shcore', use_last_error=True)
        set_awareness = shcore.SetProcessDpiAwareness
        set_awareness.argtypes = [ctypes.c_int]
        set_awareness.restype = ctypes.c_long
        result = set_awareness(2)
        if result == 0:
            return 'per-monitor'
        if result & 0xFFFFFFFF == 0x80070005:
            return 'already-configured'
    except (AttributeError, OSError):
        pass

    set_system_aware = getattr(user32, 'SetProcessDPIAware', None)
    if set_system_aware is not None:
        set_system_aware.restype = ctypes.c_bool
        if set_system_aware():
            return 'system'
    return 'unaware'


def get_window_dpi(window_handle):
    if os.name != 'nt':
        return BASE_DPI

    try:
        user32 = ctypes.WinDLL('user32', use_last_error=True)
        get_dpi = user32.GetDpiForWindow
        get_dpi.argtypes = [ctypes.c_void_p]
        get_dpi.restype = ctypes.c_uint
        return get_dpi(ctypes.c_void_p(window_handle)) or BASE_DPI
    except (AttributeError, OSError):
        return BASE_DPI


def configure_tk_scaling(root):
    dpi = get_window_dpi(root.winfo_id())
    root.tk.call('tk', 'scaling', dpi / 72.0)
    return dpi / BASE_DPI


def scale_pixels(value, scale):
    scaled_value = value * scale
    return int(scaled_value + 0.5) if scaled_value >= 0 else int(scaled_value - 0.5)


def calculate_map_scale(letter_matches, reference_distance):
    matches = [match for match in letter_matches if match[2] >= 0.6]
    candidates = []
    for first_index, first in enumerate(matches):
        for second in matches[first_index + 1:]:
            grid_delta = second[0] - first[0]
            pixel_delta = second[1] - first[1]
            if grid_delta == 0 or pixel_delta <= 0:
                continue
            pixels_per_grid = pixel_delta / grid_delta
            confidence = (min(first[2], second[2]), first[2] + second[2])
            candidates.append((confidence, pixels_per_grid))

    if reference_distance <= 0 or not candidates:
        raise ValueError('Could not identify two distinct map grid labels.')

    pixels_per_grid = max(candidates, key=lambda candidate: candidate[0])[1]
    return reference_distance / pixels_per_grid


def calculate_capture_region(client_rect, crop_region, expected_size):
    screen_x, screen_y, client_width, client_height = client_rect
    expected_width, expected_height = expected_size
    if (client_width, client_height) != (expected_width, expected_height):
        raise ValueError(
            f'Game client is {client_width}x{client_height}; '
            f'selected profile requires {expected_width}x{expected_height}.'
        )

    crop_x, crop_y, crop_width, crop_height = crop_region
    if (
        crop_x < 0
        or crop_y < 0
        or crop_width <= 0
        or crop_height <= 0
        or crop_x + crop_width > client_width
        or crop_y + crop_height > client_height
    ):
        raise ValueError('Configured minimap crop is outside the game client area.')

    return screen_x + crop_x, screen_y + crop_y, crop_width, crop_height


def get_game_capture_region(client_rect, resolution):
    profile = MAP_CAPTURE_PROFILES[resolution]
    return calculate_capture_region(
        client_rect,
        profile[:4],
        RESOLUTION_DIMENSIONS[resolution],
    )


def find_game_client_rect():
    if os.name != 'nt':
        return None

    import win32gui

    matching_windows = []

    def collect_window(window_handle, _):
        if not win32gui.IsWindowVisible(window_handle) or win32gui.IsIconic(window_handle):
            return
        if 'war thunder' not in win32gui.GetWindowText(window_handle).lower():
            return

        _, _, client_width, client_height = win32gui.GetClientRect(window_handle)
        if client_width <= 0 or client_height <= 0:
            return
        screen_x, screen_y = win32gui.ClientToScreen(window_handle, (0, 0))
        matching_windows.append((
            client_width * client_height,
            (screen_x, screen_y, client_width, client_height),
        ))

    win32gui.EnumWindows(collect_window, None)
    if not matching_windows:
        return None
    return max(matching_windows, key=lambda match: match[0])[1]