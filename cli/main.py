import click
import munch
import os
print(os.getcwd())
import task

from datetime import datetime
from common import restore
gpu_id ="2"
os.environ['CUDA_VISIBLE_DEVICES'] = gpu_id
print('export CUDA_VISIBLE_DEVICES=' + gpu_id)
#for debug running in win bat
print(os.environ['PYTHONPATH'])
def add_options(options):
    def _add_options(func):
        for option in reversed(options):
            func = option(func)
        return func
    return _add_options


@click.group(context_settings=dict(show_default=True))
@click.option('-i', '--input_path', required=True, help='Path to input image/directory.')
@click.option('-o', '--output_path', default='tmp', help='Path to output image/directory.')
@click.option('-d', '--denoiser', default='grunet', help='Denoiser type.')
@click.option('-dp', '--denoiser_path', default=r'..\models\grunet.pth', help='Path to denoiser model.')
@click.option('-s', '--solver', type=click.Choice(['admm', 'hqs']), default='admm', help='Solver type.')
@click.option('-sf', type=int, default=2, help='scaling factor (nor requared) ')
@click.option('-t',  default='with_gt', help='Type of infer - with gt or no_gt - real superres task ')

@click.option('--device', default='cuda', help='Device to use.')
@click.pass_context
def cli(ctx, input_path, output_path, denoiser, denoiser_path, solver, device, sf, t):
    ctx.ensure_object(dict)
    ctx.obj['input_path'] = input_path
    ctx.obj['output_path'] = output_path
    ctx.obj['denoiser'] = {
        'type': denoiser,
        'model_path': denoiser_path
    }
    ctx.obj['solver'] = solver
    ctx.obj['device'] = device
    ctx.obj['sf'] = sf
    ctx.obj['t'] = t


def run(task, ctx, iter, sigma, w, lam):
    ctx.obj['params'] = {

        'iter': iter,
        'sigma1': sigma[0],
        'sigma2': sigma[1],
        'w': w,
        'lam': lam
    }
    current_dir = os.getcwd()  # Get the current working directory
    parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))  # Get the parent directory
    if ctx.obj['output_path'] == 'timestamp':
        ctx.obj['output_path'] = parent_dir
        ctx.obj['output_path'] += r"\out\\"
        ctx.obj['output_path'] += datetime.now().strftime("%y%m%d_%H-%M-%S")

    cfg = munch.munchify(ctx.obj)
    restore(task, cfg)


def common_options(iter, sigma, w, lam):
    options = [
        cli.command(context_settings=dict(show_default=True)),
        click.option('-it', '--iter', default=iter, help='Number of iterations.'),
        click.option('--sigma', type=(int, int), default=sigma, help='sigma range.'),
        click.option('--w', type=float, default=w, help='weight of trade off between log and linear descent.'),
        click.option('--lam', type=float, default=lam, help='lambda.'),

              click.pass_context
    ]
    return options


@add_options(common_options(iter=24, sigma=(30, 15), w=1, lam=0.23))
def sisr(ctx, iter, sigma, w, lam):
    run(task.sisr, ctx, iter, sigma, w, lam)


@add_options(common_options(iter=24, sigma=(30, 15), w=1, lam=0.23))
def deblur(ctx, iter, sigma, w, lam):
    run(task.deblur, ctx, iter, sigma, w, lam)


@add_options(common_options(iter=24, sigma=(5, 4), w=1, lam=0.6))
def inpaint(ctx, iter, sigma, w, lam):
    run(task.inpaint, ctx, iter, sigma, w, lam)


@add_options(common_options(iter=24, sigma=(50, 45), w=1, lam=0.23))
def cs(ctx, iter, sigma, w, lam):
    run(task.cs, ctx, iter, sigma, w, lam)


@add_options(common_options(iter=24, sigma=(35, 10), w=1, lam=0.23))
def misr(ctx, iter, sigma, w, lam):
    run(task.misr, ctx, iter, sigma, w, lam)


if __name__ == '__main__':

    cli(obj={})