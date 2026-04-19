export const paths = {
  home: "/",
  talents: "/talents",
  talent: (id: string) => `/talents/${id}`,
  templates: "/templates",
  demo: "/demo",
} as const;
