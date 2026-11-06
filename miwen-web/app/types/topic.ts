export interface CreatePostDtoParams {
  title: string;
  content: string;
  cover?: string;
  forum_id?: number;
}

export interface CreatePostDto {
  id: number;
  title: string;
  content: string;
  cover: string;
  forum_id: number;
}
