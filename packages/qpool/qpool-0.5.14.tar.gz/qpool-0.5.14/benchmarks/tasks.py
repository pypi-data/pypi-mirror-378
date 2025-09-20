import pathlib
from typing import TYPE_CHECKING, Any, Optional, Tuple, Union

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


from wombat.multiprocessing import (
    produces,
    task,
)
from wombat.multiprocessing.traits.models import Task

if TYPE_CHECKING:
    from wombat.multiprocessing.worker import Worker


# --- Image Processing Helper Functions ---


def _create_initial_image(output_path: str, size: tuple[int, int], seed: int):
    """Creates a black canvas with stars."""
    rng = np.random.default_rng(seed)
    img = Image.new("RGB", size, "black")
    draw = ImageDraw.Draw(img)
    num_stars = rng.integers(100, 300)
    for _ in range(num_stars):
        x = rng.integers(0, size[0])
        y = rng.integers(0, size[1])
        brightness = rng.integers(150, 255)
        star_color = (brightness, brightness, brightness)
        star_size = rng.choice([1, 2], p=[0.8, 0.2])
        if star_size == 1:
            draw.point((x, y), fill=star_color)
        else:
            draw.ellipse((x, y, x + 1, y + 1), fill=star_color)
    img.save(output_path)


def _process_nebula_layer(
    input_path: str, output_dir: str, iteration: int, seed: int
) -> Optional[str]:
    """Adds a generative nebula layer to an image and saves it."""
    # Seed with a combination of the base seed and iteration to ensure each
    # layer is different but deterministic.
    rng = np.random.default_rng(seed + iteration)
    try:
        with Image.open(input_path) as base_img:
            base_img = base_img.convert("RGBA")
            layer = Image.new("RGBA", base_img.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(layer)
            num_clouds = rng.integers(2, 5)
            for _ in range(num_clouds):
                center_x = rng.integers(
                    -base_img.width // 4, base_img.width + base_img.width // 4
                )
                center_y = rng.integers(
                    -base_img.height // 4, base_img.height + base_img.height // 4
                )
                radius_x = (
                    rng.integers(min(base_img.size) // 4, min(base_img.size) // 2)
                    * rng.uniform(0.8, 1.2)
                )
                radius_y = (
                    rng.integers(min(base_img.size) // 4, min(base_img.size) // 2)
                    * rng.uniform(0.8, 1.2)
                )
                r, g, b = (
                    rng.integers(100, 200),
                    rng.integers(50, 150),
                    rng.integers(150, 255),
                )
                alpha = rng.integers(20, 50)
                color = (r, g, b, alpha)
                draw.ellipse(
                    (
                        center_x - radius_x,
                        center_y - radius_y,
                        center_x + radius_x,
                        center_y + radius_y,
                    ),
                    fill=color,
                )
            layer = layer.filter(
                ImageFilter.GaussianBlur(radius=max(base_img.size) / 10)
            )
            composite = Image.alpha_composite(base_img, layer)
            p = pathlib.Path(input_path)
            new_path_base = p.stem.split("_iter_")[0]
            new_path = f"{output_dir}/{new_path_base}_iter_{iteration}.png"
            composite.save(new_path)
            return new_path
    except FileNotFoundError:
        return None


def _process_starburst_effect(input_path: str, output_dir: str, seed: int) -> Optional[str]:
    """Adds a starburst effect to an image and saves it."""
    rng = np.random.default_rng(seed)
    try:
        with Image.open(input_path) as base_img:
            base_img = base_img.convert("RGBA")
            layer = Image.new("RGBA", base_img.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(layer)
            center_x, center_y = rng.integers(
                0, base_img.width
            ), rng.integers(0, base_img.height)
            num_rays = rng.integers(8, 20)
            ray_length = min(base_img.size) * rng.uniform(0.5, 1.5)
            ray_width = rng.integers(1, 4)
            color = (
                rng.integers(200, 255),
                rng.integers(200, 255),
                rng.integers(150, 255),
                rng.integers(100, 200),
            )
            for i in range(num_rays):
                angle = (i / num_rays) * 2 * np.pi
                end_x = center_x + ray_length * np.cos(angle) * rng.uniform(
                    0.5, 1.2
                )
                end_y = center_y + ray_length * np.sin(angle) * rng.uniform(
                    0.5, 1.2
                )
                draw.line(
                    [(center_x, center_y), (end_x, end_y)], fill=color, width=ray_width
                )
            layer = layer.filter(ImageFilter.GaussianBlur(radius=2))
            composite = Image.alpha_composite(base_img, layer)
            p = pathlib.Path(input_path)
            new_path_base = p.stem.split("_iter_")[0]
            new_path = f"{output_dir}/{new_path_base}_starburst.png"
            composite.save(new_path)
            return new_path
    except FileNotFoundError:
        return None


def _process_planetoid(input_path: str, output_dir: str, seed: int) -> Optional[str]:
    """Adds a planetoid to an image and saves it."""
    rng = np.random.default_rng(seed)
    try:
        with Image.open(input_path) as base_img:
            base_img = base_img.convert("RGBA")
            layer = Image.new("RGBA", base_img.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(layer)
            px, py = rng.integers(0, base_img.width), rng.integers(
                0, base_img.height
            )
            prad = rng.integers(
                min(base_img.size) // 10, min(base_img.size) // 4
            )
            r, g, b = rng.integers(50, 200, 3)
            draw.ellipse(
                (px - prad, py - prad, px + prad, py + prad), fill=(r, g, b, 255)
            )
            for _ in range(50):
                angle = rng.uniform(0, 2 * np.pi)
                dist = rng.uniform(0, prad)
                tx, ty = int(px + dist * np.cos(angle)), int(py + dist * np.sin(angle))
                shade = rng.integers(-30, 30)
                draw.point((tx, ty), fill=(r + shade, g + shade, b + shade, 255))
            layer = layer.filter(ImageFilter.GaussianBlur(radius=1))
            composite = Image.alpha_composite(base_img, layer)
            p = pathlib.Path(input_path)
            new_path_base = p.stem.split("_iter_")[0]
            new_path = f"{output_dir}/{new_path_base}_planetoid.png"
            composite.save(new_path)
            return new_path
    except FileNotFoundError:
        return None


# --- Wombat Task Actions ---


@produces()
@task
def add_nebula_layer(
    _worker: "Worker",
    input_path: str,
    output_dir: str,
    iteration: int,
    max_iterations: int,
    seed: int,
) -> Optional[Union[Task, list[Task]]]:
    """
    Adds a generative layer to an image, simulating a nebula effect.
    After a few layers, this task can branch, producing multiple new tasks.
    """
    new_path = _process_nebula_layer(
        input_path=input_path, output_dir=output_dir, iteration=iteration, seed=seed
    )
    if not new_path:
        return None

    # After a few layers, fan out into many simple tasks.
    if iteration >= max_iterations:
        # This is a fan-out test. One task produces many simple, terminal tasks.
        # Wombat's @produces trait handles this efficiently inside the worker,
        # while concurrent.futures must process all results and schedule all
        # new tasks in the single, main orchestrator thread, creating a bottleneck.
        num_final_tasks = 100
        return [final_success_task(input_path=new_path) for _ in range(num_final_tasks)]

    # Continue the linear pipeline for the first few layers.
    return add_nebula_layer(
        input_path=new_path,
        output_dir=output_dir,
        iteration=iteration + 1,
        max_iterations=max_iterations,
        seed=seed,
    )


@produces()
@task
def add_starburst_effect(
    _worker: "Worker", input_path: str, output_dir: str, seed: int
) -> Optional[Task]:
    """Adds a bright starburst/lens flare effect to the image."""
    new_path = _process_starburst_effect(
        input_path=input_path, output_dir=output_dir, seed=seed
    )
    if new_path:
        return final_success_task(input_path=new_path)
    return None


@produces()
@task
def add_planetoid(
    _worker: "Worker", input_path: str, output_dir: str, seed: int
) -> Optional[Task]:
    """Adds a small, textured planetoid to the image."""
    new_path = _process_planetoid(input_path=input_path, output_dir=output_dir, seed=seed)
    if new_path:
        return final_success_task(input_path=new_path)
    return None


@produces()
@task
def start_nebula_pipeline(
    _worker: "Worker",
    output_path: str,
    size: tuple[int, int],
    max_iterations: int,
    seed: int,
) -> Task:
    """
    Creates a black canvas with stars and kicks off one of several possible
    image processing pipelines.
    """
    _create_initial_image(output_path=output_path, size=size, seed=seed)
    output_dir = str(pathlib.Path(output_path).parent)

    # Use the seed for a deterministic "random" choice.
    rng = np.random.default_rng(seed)
    choice = rng.choice([0, 1, 2])

    if choice == 0:
        # The nebula pipeline fans out into many final tasks.
        return add_nebula_layer(
            input_path=output_path,
            output_dir=output_dir,
            iteration=1,
            max_iterations=max_iterations,
            seed=seed,
        )
    elif choice == 1:
        # The starburst pipeline is a single, terminal task.
        return add_starburst_effect(
            input_path=output_path,
            output_dir=output_dir,
            seed=seed,
        )
    else:  # choice == 2
        # The planetoid pipeline is a single, terminal task.
        return add_planetoid(
            input_path=output_path,
            output_dir=output_dir,
            seed=seed,
        )


@task
def final_success_task(_worker: "Worker", input_path: str) -> str:
    """A terminal task that signals a successful pipeline completion."""
    return input_path


# --- concurrent.futures compatible task functions ---


def add_nebula_layer_cf(
    input_path: str,
    output_dir: str,
    iteration: int,
    max_iterations: int,
    seed: int,
) -> Any:  # Returns Union[None, tuple, list[tuple]]
    """
    concurrent.futures version of add_nebula_layer.
    Can return a list of next actions to simulate branching.
    """
    new_path = _process_nebula_layer(
        input_path=input_path, output_dir=output_dir, iteration=iteration, seed=seed
    )
    if not new_path:
        return None

    # After a few layers, fan out into many simple tasks.
    if iteration >= max_iterations:
        # This is a fan-out test. The single result from this task will be a list
        # of 100 new tasks that the main thread must schedule, creating a bottleneck.
        num_final_tasks = 100
        return [
            ("final_success_task_cf", {"input_path": new_path})
            for _ in range(num_final_tasks)
        ]

    # Continue linear pipeline for first few layers
    return "add_nebula_layer_cf", {
        "input_path": new_path,
        "output_dir": output_dir,
        "iteration": iteration + 1,
        "max_iterations": max_iterations,
        "seed": seed,
    }


def add_starburst_effect_cf(
    input_path: str, output_dir: str, seed: int
) -> Optional[Tuple[str, dict[str, Any]]]:
    """concurrent.futures version of add_starburst_effect."""
    new_path = _process_starburst_effect(
        input_path=input_path, output_dir=output_dir, seed=seed
    )
    if new_path:
        return "final_success_task_cf", {"input_path": new_path}
    return None


def add_planetoid_cf(
    input_path: str, output_dir: str, seed: int
) -> Optional[Tuple[str, dict[str, Any]]]:
    """concurrent.futures version of add_planetoid."""
    new_path = _process_planetoid(input_path=input_path, output_dir=output_dir, seed=seed)
    if new_path:
        return "final_success_task_cf", {"input_path": new_path}
    return None


def start_nebula_pipeline_cf(
    output_path: str, size: tuple[int, int], max_iterations: int, seed: int
) -> Tuple[str, dict[str, Any]]:
    """concurrent.futures version of start_nebula_pipeline."""
    _create_initial_image(output_path=output_path, size=size, seed=seed)
    output_dir = str(pathlib.Path(output_path).parent)

    # Use the seed for a deterministic "random" choice.
    rng = np.random.default_rng(seed)
    choice = rng.choice([0, 1, 2])

    if choice == 0:
        # The nebula pipeline fans out into many final tasks.
        return "add_nebula_layer_cf", {
            "input_path": output_path,
            "output_dir": output_dir,
            "iteration": 1,
            "max_iterations": max_iterations,
            "seed": seed,
        }
    elif choice == 1:
        # The starburst pipeline is a single, terminal task.
        return "add_starburst_effect_cf", {
            "input_path": output_path,
            "output_dir": output_dir,
            "seed": seed,
        }
    else:  # choice == 2
        # The planetoid pipeline is a single, terminal task.
        return "add_planetoid_cf", {
            "input_path": output_path,
            "output_dir": output_dir,
            "seed": seed,
        }


def final_success_task_cf(input_path: str) -> str:
    """concurrent.futures version of final_success_task."""
    return input_path
