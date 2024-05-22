import argparse

from AIROB.domain import PDDLEnvironment
from .Dryer import Dryer
from .Cube import Cube
from .Brush import Brush
from .Color import Color
from .Robot import Robot


def args():
    parser = argparse.ArgumentParser(prog='Cubeotta')
    parser.add_argument('--cubes', type=int, default=2, help='number of cubes')
    return parser


def create_env(env: PDDLEnvironment, args):
    for i in range(args.cubes):
        env.add_object(Cube(i))

    env.add_object(Dryer(0))
    env.add_object(Brush(0))
    env.add_object(Color("red"))  # for the time being we assume that we only have one color
    env.add_object(Robot())  # we must have one single instance of Robot
    return env
