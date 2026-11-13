import adapter from '@sveltejs/adapter-static';

const output = process.env.WEB_OUTPUT_DIR ?? 'build';

export default {
  kit: {
    adapter: adapter({ pages: output, assets: output }),
    paths: { base: process.env.SITE_BASE_PATH ?? '' },
  },
};
