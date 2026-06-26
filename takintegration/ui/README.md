# TAK Module Federation Component

## Development

### rmdev/rmlocal

Federated components are built when rmdev or rmlocal is built. In rmdev the component is rebuilt after any changes. To see the changes just refresh your browser.

### Using Vite dev server

You can also develop components with just the vite dev server, but this is only recommended for simpler components.

Install dependencies and start the dev server:

```bash
pnpm install
pnpm dev
```

Component runs locally at: [http://localhost:4174/](http://localhost:4174/)

## Assets

Place assets in the `public/` folder, for example:

```
public/taistelija.png
```

When using these assets in code **always** prefix them with `/ui/{shortProductName}/`. for example:

```
/ui/tak/taistelija.png
```

This is required due to how things are included in the production. `vite.config.ts` rewrites the routes if using vite dev server.

## Getting data to the component

DeployApp automatically fetches and passes user data for the component as props (if the API provides it). In federated components, it is possible to do API calls to other required endpoints.

If developing simple components using just the vite dev server, you can fetch the user data from the api. For example:

```
https://localmaeher.dev.pvarki.fi:4439/api/v2/instructions/data/tak
```

Paste the entire response into `src/main.tsx` as the value of `SAMPLE_DATA`.

It is recommended to test what happens if no data is passed as it might take a while for the api to return data.

## Styles

`src/index.css` should reflect the styles of the main UI. It could be outdated, so it might be worth while to copy the file from the main UI here every once in a while.

This file is **not** included in the production build. It is only used to make development with the vite dev server possible. In production or rmdev the styles of main UI are used.
