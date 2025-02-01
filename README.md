# Anagrams

## Install and Run

### Prerequisites

#### [`just`](https://github.com/casey/just)

`just` is a development utility to run scripts (a.k.a. 'recipes')
defined in the [`justfile`](./justfile). More info below.

#### [`npm`](https://github.com/npm/cli)

`npm` manages `node`, and is used to build the frontend of the app.

#### [`uv`](https://github.com/astral-sh/uv)

`uv` manages python installations and packages, and is used to run 
the backend of the app.

> [!TIP]
> For mac users, all three of these prerequisites 
> can be installed with homebrew:
>
>`brew install just node uv`

### Running the App

After installing all the prerequisites above, clone this repository
and run with `just run`:

```sh
git clone https://github.com/ianbulovic/anagrams
cd anagrams
just run # build and run the app
```

## Development

Run `just dev` to run in development mode, which will enables auto-reload
for both the backend and the frontend.

Run `just help` to see more development recipes.