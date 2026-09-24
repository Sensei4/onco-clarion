export interface MmsEntity {
  uri: string;
  the_code: string;
  title: string;
  chapter: string;
  is_leaf: boolean;
  synonyms: string[];
  foundation_uri: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface SearchParams {
  q: string;
  chapter?: string;
  page?: number;
  page_size?: number;
}

export interface ChapterCount {
  chapter: string;
  count: number;
}
