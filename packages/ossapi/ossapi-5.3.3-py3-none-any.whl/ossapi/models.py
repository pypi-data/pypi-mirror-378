# opt-in to forward type annotations
# https://docs.python.org/3.7/whatsnew/3.7.html#pep-563-postponed-evaluation-
# of-annotations
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Generic, Optional, TypeVar, Union

from ossapi.enums import (
    Availability,
    BeatmapOwner,
    BeatmapPackUserCompletionData,
    BeatmapsetApproval,
    BeatmapsetEventType,
    BeatmapTag,
    ChangelogSearch,
    ChannelType,
    Country,
    Cover,
    Covers,
    EventAchivement,
    EventBeatmap,
    EventBeatmapset,
    EventType,
    EventUser,
    Failtimes,
    ForumPollText,
    ForumPollTitle,
    ForumPostBody,
    ForumTopicSort,
    ForumTopicType,
    GameMode,
    GithubUser,
    Grade,
    Hype,
    Kudosu,
    KudosuAction,
    KudosuGiver,
    KudosuPost,
    KudosuVote,
    MatchEventType,
    MessageType,
    NewsSearch,
    Nomination,
    Nominations,
    PlayStyles,
    ProfileBanner,
    ProfilePage,
    RankHighest,
    RankHistory,
    RankStatus,
    ReviewsConfig,
    RoomCategory,
    RoomDifficultyRange,
    RoomPlaylistItemStats,
    RoomType,
    ScoringType,
    Statistics,
    Team,
    TeamType,
    UserAccountHistory,
    UserAchievement,
    UserBadge,
    UserGradeCounts,
    UserGroup,
    UserLevel,
    UserMonthlyPlaycount,
    UserPage,
    UserProfileCustomization,
    UserRelationType,
    UserReplaysWatchedCount,
    Variant,
    Weight,
)
from ossapi.mod import Mod
from ossapi.utils import BaseModel, Datetime, Field, Model

T = TypeVar("T")
S = TypeVar("S")

"""
a type hint of ``Optional[Any]`` or ``Any`` means that I don't know what type it
is, not that the api actually lets any type be returned there.
"""

# =================
# Documented Models
# =================

# the weird location of the cursor class and `CursorT` definition is to remove
# the need for forward type annotations, which breaks typing_utils when they
# try to evaluate the forwardref (as the `Cursor` class is not in scope at that
# moment). We would be able to fix this by manually passing forward refs to the
# lib instead, but I don't want to have to keep track of which forward refs need
# passing and which don't, or which classes I need to import in various files
# (it's not as simple as just sticking a `global()` call in and calling it a
# day). So I'm just going to ban forward refs in the codebase for now, until we
# want to drop typing_utils (and thus support for python 3.8 and lower).
# It's also possible I'm missing an obvious fix for this, but I suspect this is
# a limitation of older python versions.

# Cursors are an interesting case. As I understand it, they don't have a
# predefined set of attributes across all endpoints, but instead differ per
# endpoint. I don't want to have dozens of different cursor classes (although
# that would perhaps be the proper way to go about this), so just allow
# any attribute.
# This is essentially a reimplementation of SimpleNamespace to deal with
# BaseModels being passed the data as a single dict (`_data`) instead of as
# **kwargs, plus some other weird stuff we're doing like handling cursor
# objects being passed as data
# We want cursors to also be instantiatable manually (eg `Cursor(page=199)`),
# so make `_data` optional and also allow arbitrary `kwargs`.


class Cursor(BaseModel):
    def __init__(self, _data=None, **kwargs):
        super().__init__()
        # allow Cursor to be instantiated with another cursor as a no-op
        if isinstance(_data, Cursor):
            _data = _data.__dict__
        _data = _data or kwargs
        self.__dict__.update(_data)

    def __repr__(self):
        keys = sorted(self.__dict__)
        items = (f"{k}={self.__dict__[k]!r}" for k in keys)
        return f"{type(self).__name__}({', '.join(items)})"

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


# if there are no more results, a null cursor is returned instead.
# So always let the cursor be nullable to catch this. It's the user's
# responsibility to check for a null cursor to see if there are any more
# results.
CursorT = Optional[Cursor]
CursorStringT = Optional[str]


class UserCompact(Model):
    """
    https://osu.ppy.sh/docs/index.html#usercompact
    """

    # required fields
    # ---------------
    avatar_url: str
    country_code: str
    id: int
    is_active: bool
    is_bot: bool
    is_deleted: bool
    is_online: bool
    is_supporter: bool
    last_visit: Optional[Datetime]
    pm_friends_only: bool
    profile_colour: Optional[str]
    username: str

    # optional fields
    # ---------------
    account_history: Optional[list[UserAccountHistory]]
    active_tournament_banner: Optional[ProfileBanner]
    active_tournament_banners: Optional[list[ProfileBanner]]
    badges: Optional[list[UserBadge]]
    beatmap_playcounts_count: Optional[int]
    blocks: Optional[UserRelation]
    country: Optional[Country]
    cover: Optional[Cover]
    default_group: Optional[str]
    favourite_beatmapset_count: Optional[int]
    follow_user_mapping: Optional[list[int]]
    follower_count: Optional[int]
    friends: Optional[list[UserRelation]]
    graveyard_beatmapset_count: Optional[int]
    groups: Optional[list[UserGroup]]
    guest_beatmapset_count: Optional[int]
    is_restricted: Optional[bool]
    is_silenced: Optional[bool]
    loved_beatmapset_count: Optional[int]
    # undocumented
    mapping_follower_count: Optional[int]
    monthly_playcounts: Optional[list[UserMonthlyPlaycount]]
    page: Optional[UserPage]
    pending_beatmapset_count: Optional[int]
    previous_usernames: Optional[list[str]]
    # deprecated, replaced by rank_history
    rankHistory: Optional[RankHistory]
    rank_history: Optional[RankHistory]
    # deprecated, replaced by ranked_beatmapset_count
    ranked_and_approved_beatmapset_count: Optional[int]
    ranked_beatmapset_count: Optional[int]
    replays_watched_counts: Optional[list[UserReplaysWatchedCount]]
    scores_best_count: Optional[int]
    scores_first_count: Optional[int]
    scores_recent_count: Optional[int]
    statistics: Optional[UserStatistics]
    statistics_rulesets: Optional[UserStatisticsRulesets]
    support_level: Optional[int]
    # deprecated, replaced by pending_beatmapset_count
    unranked_beatmapset_count: Optional[int]
    unread_pm_count: Optional[int]
    user_achievements: Optional[list[UserAchievement]]
    user_preferences: Optional[UserProfileCustomization]
    session_verified: Optional[bool]
    team: Optional[Team]

    def expand(self) -> User:
        return self._fk_user(self.id)


class User(UserCompact):
    comments_count: int
    cover_url: str
    discord: Optional[str]
    has_supported: bool
    interests: Optional[str]
    join_date: Datetime
    kudosu: Kudosu
    location: Optional[str]
    max_blocks: int
    max_friends: int
    occupation: Optional[str]
    playmode: str
    playstyle: Optional[PlayStyles]
    post_count: int
    profile_order: list[ProfilePage]
    profile_hue: Optional[int]
    daily_challenge_user_stats: DailyChallengeUserStats
    title: Optional[str]
    title_url: Optional[str]
    twitter: Optional[str]
    website: Optional[str]
    scores_pinned_count: int
    nominated_beatmapset_count: int
    rank_highest: Optional[RankHighest]
    current_season_stats: Optional[SeasonStatistics]

    def expand(self) -> User:
        # we're already expanded, no need to waste an api call
        return self


class BeatmapCompact(Model):
    # required fields
    # ---------------
    difficulty_rating: float
    id: int
    mode: GameMode
    status: RankStatus
    total_length: int
    version: str
    user_id: int
    beatmapset_id: int

    # optional fields
    # ---------------
    _beatmapset: Field(name="beatmapset", type=Optional[BeatmapsetCompact])
    checksum: Optional[str]
    failtimes: Optional[Failtimes]
    max_combo: Optional[int]

    def expand(self) -> Beatmap:
        return self._fk_beatmap(self.id)

    def user(self) -> User:
        return self._fk_user(self.user_id)

    def beatmapset(self) -> Union[Beatmapset, BeatmapsetCompact]:
        return self._fk_beatmapset(self.beatmapset_id, existing=self._beatmapset)


class Beatmap(BeatmapCompact):
    total_length: int
    version: str
    accuracy: float
    ar: float
    bpm: Optional[float]
    current_user_tag_ids: list[int]
    # this might be non-optional? should test with client credentials grant.
    current_user_playcount: Optional[int]
    top_tag_ids: list[int]
    convert: bool
    count_circles: int
    count_sliders: int
    count_spinners: int
    cs: float
    deleted_at: Optional[Datetime]
    drain: float
    hit_length: int
    is_scoreable: bool
    last_updated: Datetime
    mode_int: int
    rating: float
    passcount: int
    playcount: int
    ranked: RankStatus
    url: str
    # user associated with this difficulty (ie diff mapper / owner).
    # Returned as `user` in the api, but that conflicts with our fk method for
    # beatmapset owner.
    # This is optional as a workaround until
    # https://github.com/ppy/osu-web/issues/9784 is resolved.
    owner: Field(name="user", type=Optional[UserCompact])
    # TODO does the new addition of this owners attribute deprecate the owner
    # attribute?
    owners: Optional[list[BeatmapOwner]]

    # overridden fields
    # -----------------
    _beatmapset: Field(name="beatmapset", type=Optional[Beatmapset])

    def expand(self) -> Beatmap:
        return self

    def beatmapset(self) -> Beatmapset:
        return self._fk_beatmapset(self.beatmapset_id, existing=self._beatmapset)


class BeatmapsetCompact(Model):
    """
    https://osu.ppy.sh/docs/index.html#beatmapsetcompact
    """

    # required fields
    # ---------------
    artist: str
    artist_unicode: str
    covers: Covers
    current_user_playcount: int
    creator: str
    favourite_count: int
    id: int
    nsfw: bool
    offset: int
    play_count: int
    preview_url: str
    source: str
    status: RankStatus
    spotlight: bool
    title: str
    title_unicode: str
    user_id: int
    video: bool
    # documented as being in `Beatmapset` only, but returned by
    # `api.beatmapset_events` which uses a `BeatmapsetCompact`.
    hype: Optional[Hype]

    # optional fields
    # ---------------
    beatmaps: Optional[list[Beatmap]]
    converts: Optional[Any]
    current_nominations: Optional[list[Nomination]]
    current_user_attributes: Optional[Any]
    description: Optional[Any]
    discussions: Optional[Any]
    events: Optional[Any]
    genre: Optional[Any]
    has_favourited: Optional[bool]
    language: Optional[Any]
    nominations: Optional[Any]
    pack_tags: Optional[list[str]]
    ratings: Optional[Any]
    recent_favourites: Optional[Any]
    related_users: Optional[Any]
    track_id: Optional[int]
    _user: Field(name="user", type=Optional[UserCompact])

    def expand(self) -> Beatmapset:
        return self._fk_beatmapset(self.id)

    def user(self) -> Union[UserCompact, User]:
        return self._fk_user(self.user_id, existing=self._user)


class Beatmapset(BeatmapsetCompact):
    availability: Availability
    bpm: float
    can_be_hyped: bool
    deleted_at: Optional[Datetime]
    discussion_enabled: bool
    discussion_locked: bool
    is_scoreable: bool
    last_updated: Datetime
    legacy_thread_url: Optional[str]
    nominations_summary: Nominations
    ranked: RankStatus
    ranked_date: Optional[Datetime]
    rating: float
    storyboard: bool
    submitted_date: Optional[Datetime]
    tags: str
    related_tags: list[BeatmapTag]

    def expand(self) -> Beatmapset:
        return self


# undocumented, but defined here to avoid a forward reference in Score.
class ScoreMatchInfo(Model):
    slot: int
    team: str
    pass_: Field(name="pass", type=bool)


class _LegacyScore(Model):
    # can be null for match scores, eg the scores
    # in https://osu.ppy.sh/community/matches/97947404
    id: Optional[int]
    best_id: Optional[int]
    user_id: int
    accuracy: float
    mods: Mod
    score: int
    max_combo: int
    perfect: bool
    statistics: Statistics
    pp: Optional[float]
    rank: Grade
    created_at: Datetime
    mode: GameMode
    mode_int: int
    replay: bool
    passed: bool
    current_user_attributes: Any
    beatmap: Optional[Beatmap]
    beatmapset: Optional[BeatmapsetCompact]
    rank_country: Optional[int]
    rank_global: Optional[int]
    weight: Optional[Weight]
    _user: Field(name="user", type=Optional[UserCompact])
    match: Optional[ScoreMatchInfo]
    type: str


class Score(Model):
    """
    https://osu.ppy.sh/docs/index.html#score with x-api-version >= 20220705
    """

    id: Optional[int]
    best_id: Optional[int]
    user_id: int
    accuracy: float
    max_combo: int
    statistics: Statistics
    pp: Optional[float]
    rank: Grade

    passed: bool
    current_user_attributes: Any
    classic_total_score: int
    processed: bool
    replay: bool
    maximum_statistics: Statistics
    mods: list[NonLegacyMod]
    ruleset_id: int
    started_at: Optional[Datetime]
    ended_at: Datetime
    ranked: bool
    preserve: bool
    beatmap_id: int
    build_id: Optional[int]
    has_replay: bool
    is_perfect_combo: bool
    total_score: int
    total_score_without_mods: Optional[int]

    legacy_perfect: bool
    legacy_score_id: Optional[int]
    legacy_total_score: int

    beatmap: Optional[Beatmap]
    beatmapset: Optional[BeatmapsetCompact]
    rank_country: Optional[int]
    rank_global: Optional[int]
    weight: Optional[Weight]
    _user: Field(name="user", type=Optional[UserCompact])
    match: Optional[ScoreMatchInfo]
    type: str

    @staticmethod
    def override_attributes(data, api):
        if api.api_version < 20220705:
            return _LegacyScore
        # there are rare cases where a legacy score is returned even when using a
        # modern api version. Legacy matches is the only exception I'm aware of currently.
        #
        # check a few attributes to be reasonably certain that we are in this case,
        # and then switch to _LegacyScore.
        if "mode" in data and "created_at" in data and "legacy_perfect" not in data:
            return _LegacyScore

    @staticmethod
    def preprocess_data(data, api):
        # scores from matches (api.match) return perfect as an int instead of a
        # bool (same as api v1). Convert to a bool here.
        if "perfect" in data and isinstance(data["perfect"], int):
            data["perfect"] = bool(data["perfect"])
        return data

    def user(self) -> Union[UserCompact, User]:
        return self._fk_user(self.user_id, existing=self._user)

    def download(self):
        if hasattr(self, "mode"):
            # _LegacyScore
            return self._api.download_score_mode(self.mode, self.id)

        return self._api.download_score(self.id)


class BeatmapUserScore(Model):
    position: int
    score: Score


class BeatmapUserScores(Model):
    scores: list[Score]


class BeatmapScores(Model):
    scores: list[Score]
    score_count: int
    user_score: Field(name="userScore", type=Optional[BeatmapUserScore])


class CommentableMeta(Model):
    # title is the only attribute returned for deleted commentables.
    id: Optional[int]
    title: str
    type: Optional[str]
    url: Optional[str]
    owner_id: Optional[int]
    owner_title: Optional[str]
    current_user_attributes: Optional[CommentableMetaCurrentUserAttributes]


class CommentableMetaCurrentUserAttributes(Model):
    can_new_comment_reason: Optional[str]


class Comment(Model):
    # null for deleted commentables, eg on /comments/3.
    commentable_id: Optional[int]
    # null for deleted commentables, eg on /comments/3.
    commentable_type: Optional[str]
    created_at: Datetime
    deleted_at: Optional[Datetime]
    edited_at: Optional[Datetime]
    edited_by_id: Optional[int]
    id: int
    legacy_name: Optional[str]
    message: Optional[str]
    message_html: Optional[str]
    parent_id: Optional[int]
    pinned: bool
    replies_count: int
    updated_at: Datetime
    # null for some commentables, eg on /comments/3.
    user_id: Optional[int]
    votes_count: int

    def user(self) -> User:
        return self._fk_user(self.user_id)

    def edited_by(self) -> Optional[User]:
        return self._fk_user(self.edited_by_id)


class CommentBundle(Model):
    commentable_meta: list[CommentableMeta]
    comments: list[Comment]
    cursor: CursorT
    has_more: bool
    has_more_id: Optional[int]
    included_comments: list[Comment]
    pinned_comments: Optional[list[Comment]]
    # TODO this should be type CommentSort
    sort: str
    top_level_count: Optional[int]
    total: Optional[int]
    user_follow: bool
    user_votes: list[int]
    users: list[UserCompact]


class ForumPost(Model):
    created_at: Datetime
    deleted_at: Optional[Datetime]
    edited_at: Optional[Datetime]
    edited_by_id: Optional[int]
    forum_id: int
    id: int
    topic_id: int
    user_id: int
    body: ForumPostBody

    def user(self) -> User:
        return self._fk_user(self.user_id)

    def edited_by(self) -> Optional[User]:
        return self._fk_user(self.edited_by_id)


class ForumTopic(Model):
    created_at: Datetime
    deleted_at: Optional[Datetime]
    first_post_id: int
    forum_id: int
    id: int
    is_locked: bool
    last_post_id: int
    post_count: int
    title: str
    type: ForumTopicType
    updated_at: Datetime
    user_id: int
    poll: Optional[ForumPollModel]

    def user(self) -> User:
        return self._fk_user(self.user_id)


class ForumPollModel(Model):
    allow_vote_change: bool
    ended_at: Optional[Datetime]
    hide_incomplete_results: bool
    last_vote_at: Optional[Datetime]
    max_votes: int
    options: list[ForumPollOption]
    started_at: Datetime
    title: ForumPollTitle
    total_vote_count: int


class ForumPollOption(Model):
    id: int
    text: ForumPollText
    vote_count: Optional[int]


class ForumTopicAndPosts(Model):
    cursor: CursorT
    search: ForumTopicSearch
    posts: list[ForumPost]
    topic: ForumTopic
    cursor_string: CursorStringT


class CreateForumTopicResponse(Model):
    post: ForumPost
    topic: ForumTopic


class ForumTopicSearch(Model):
    sort: Optional[ForumTopicSort]
    limit: Optional[int]
    start: Optional[int]
    end: Optional[int]


class SearchResult(Generic[T], Model):
    data: list[T]
    total: int


class WikiPage(Model):
    layout: str
    locale: str
    markdown: str
    path: str
    subtitle: Optional[str]
    tags: list[str]
    title: str
    available_locales: list[str]


class Search(Model):
    users: Field(name="user", type=Optional[SearchResult[UserCompact]])
    wiki_pages: Field(name="wiki_page", type=Optional[SearchResult[WikiPage]])


class Spotlight(Model):
    end_date: Datetime
    id: int
    mode_specific: bool
    participant_count: Optional[int]
    name: str
    start_date: Datetime
    type: str


class Spotlights(Model):
    spotlights: list[Spotlight]


class SeasonDivision(Model):
    colour_tier: str
    id: int
    image_url: str
    name: str
    threshold: float


class Season(Model):
    start_date: Datetime
    end_date: Optional[Datetime]
    name: str
    room_count: int


class SeasonStatistics(Model):
    division: SeasonDivision
    season: Season
    rank: int
    total_score: float


# return-value wrapper for https://osu.ppy.sh/docs/index.html#get-users.
class Users(Model):
    users: list[UserCompact]


# return-value wrapper for https://osu.ppy.sh/docs/index.html#get-beatmaps.
class Beatmaps(Model):
    beatmaps: list[Beatmap]


class BeatmapPacks(Model):
    cursor: CursorT
    cursor_string: CursorStringT
    beatmap_packs: list[BeatmapPack]


class Rankings(Model):
    beatmapsets: Optional[list[Beatmapset]]
    cursor: CursorT
    cursor_string: Optional[str]
    ranking: Union[list[UserStatistics], list[CountryStatistics]]
    spotlight: Optional[Spotlight]
    total: Optional[int]


class BeatmapsetDiscussionPost(Model):
    id: int
    beatmapset_discussion_id: int
    user_id: int
    last_editor_id: Optional[int]
    deleted_by_id: Optional[int]
    system: bool
    message: str
    created_at: Datetime
    updated_at: Datetime
    deleted_at: Optional[Datetime]

    def user(self) -> User:
        return self._fk_user(self.user_id)

    def last_editor(self) -> Optional[User]:
        return self._fk_user(self.last_editor_id)

    def deleted_by(self) -> Optional[User]:
        return self._fk_user(self.deleted_by_id)


class BeatmapsetDiscussion(Model):
    id: int
    beatmapset_id: int
    beatmap_id: Optional[int]
    user_id: int
    deleted_by_id: Optional[int]
    message_type: MessageType
    parent_id: Optional[int]
    # a point of time which is ``timestamp`` milliseconds into the map
    timestamp: Optional[int]
    resolved: bool
    can_be_resolved: bool
    can_grant_kudosu: bool
    created_at: Datetime
    current_user_attributes: Any
    updated_at: Datetime
    deleted_at: Optional[Datetime]
    # marked as required in the docs, but null in
    #   api.beatmapset_events(beatmapset_id=1112418)
    # due to this post
    # https://osu.ppy.sh/beatmapsets/1112418/discussion/-/generalAll#/1633002
    last_post_at: Optional[Datetime]
    kudosu_denied: bool
    starting_post: Optional[BeatmapsetDiscussionPost]
    posts: Optional[list[BeatmapsetDiscussionPost]]
    _beatmap: Field(name="beatmap", type=Optional[BeatmapCompact])
    _beatmapset: Field(name="beatmapset", type=Optional[BeatmapsetCompact])

    def user(self) -> User:
        return self._fk_user(self.user_id)

    def deleted_by(self) -> Optional[User]:
        return self._fk_user(self.deleted_by_id)

    def beatmapset(self) -> Union[Beatmapset, BeatmapsetCompact]:
        return self._fk_beatmapset(self.beatmapset_id, existing=self._beatmapset)

    def beatmap(self) -> Union[Optional[Beatmap], BeatmapCompact]:
        return self._fk_beatmap(self.beatmap_id, existing=self._beatmap)


class BeatmapsetDiscussionVote(Model):
    id: int
    score: int
    user_id: int
    beatmapset_discussion_id: int
    created_at: Datetime
    updated_at: Datetime
    # TODO is this field ever actually returned? not documented and can't find
    # a repro case.
    cursor_string: CursorStringT

    def user(self):
        return self._fk_user(self.user_id)


class KudosuHistory(Model):
    id: int
    action: KudosuAction
    amount: int
    # TODO enumify this. Described as "Object type which the exchange happened
    # on (forum_post, etc)." in https://osu.ppy.sh/docs/index.html#kudosuhistory
    model: str
    created_at: Datetime
    giver: Optional[KudosuGiver]
    post: KudosuPost
    # see https://github.com/ppy/osu-web/issues/7549
    details: Any


class BeatmapPlaycount(Model):
    beatmap_id: int
    _beatmap: Field(name="beatmap", type=Optional[BeatmapCompact])
    beatmapset: Optional[BeatmapsetCompact]
    count: int

    def beatmap(self) -> Union[Beatmap, BeatmapCompact]:
        return self._fk_beatmap(self.beatmap_id, existing=self._beatmap)


# we use this class to determine which event dataclass to instantiate and
# return, based on the value of the ``type`` parameter.
class _Event(Model):
    @staticmethod
    def override_attributes(data, api):
        mapping = {
            EventType.ACHIEVEMENT: AchievementEvent,
            EventType.BEATMAP_PLAYCOUNT: BeatmapPlaycountEvent,
            EventType.BEATMAPSET_APPROVE: BeatmapsetApproveEvent,
            EventType.BEATMAPSET_DELETE: BeatmapsetDeleteEvent,
            EventType.BEATMAPSET_REVIVE: BeatmapsetReviveEvent,
            EventType.BEATMAPSET_UPDATE: BeatmapsetUpdateEvent,
            EventType.BEATMAPSET_UPLOAD: BeatmapsetUploadEvent,
            EventType.RANK: RankEvent,
            EventType.RANK_LOST: RankLostEvent,
            EventType.USER_SUPPORT_FIRST: UserSupportFirstEvent,
            EventType.USER_SUPPORT_AGAIN: UserSupportAgainEvent,
            EventType.USER_SUPPORT_GIFT: UserSupportGiftEvent,
            EventType.USERNAME_CHANGE: UsernameChangeEvent,
        }
        type_ = EventType(data["type"])
        return mapping[type_]


class Event(Model):
    created_at: Datetime
    createdAt: Datetime
    id: int
    type: EventType


class AchievementEvent(Event):
    achievement: EventAchivement
    user: EventUser


class BeatmapPlaycountEvent(Event):
    beatmap: EventBeatmap
    count: int


class BeatmapsetApproveEvent(Event):
    approval: BeatmapsetApproval
    beatmapset: EventBeatmapset
    user: EventUser


class BeatmapsetDeleteEvent(Event):
    beatmapset: EventBeatmapset


class BeatmapsetReviveEvent(Event):
    beatmapset: EventBeatmapset
    user: EventUser


class BeatmapsetUpdateEvent(Event):
    beatmapset: EventBeatmapset
    user: EventUser


class BeatmapsetUploadEvent(Event):
    beatmapset: EventBeatmapset
    user: EventUser


class RankEvent(Event):
    scoreRank: str
    rank: int
    mode: GameMode
    beatmap: EventBeatmap
    user: EventUser


class RankLostEvent(Event):
    mode: GameMode
    beatmap: EventBeatmap
    user: EventUser


class UserSupportFirstEvent(Event):
    user: EventUser


class UserSupportAgainEvent(Event):
    user: EventUser


class UserSupportGiftEvent(Event):
    user: EventUser


class UsernameChangeEvent(Event):
    user: EventUser


class Build(Model):
    created_at: Datetime
    display_version: str
    id: int
    update_stream: Optional[UpdateStream]
    users: int
    version: Optional[str]
    changelog_entries: Optional[list[ChangelogEntry]]
    versions: Optional[Versions]
    youtube_id: Optional[str]


class Versions(Model):
    next: Optional[Build]
    previous: Optional[Build]


class UpdateStream(Model):
    display_name: Optional[str]
    id: int
    is_featured: bool
    name: str
    latest_build: Optional[Build]
    user_count: Optional[int]


class ChangelogEntry(Model):
    category: str
    created_at: Optional[Datetime]
    github_pull_request_id: Optional[int]
    github_url: Optional[str]
    id: Optional[int]
    major: bool
    message: Optional[str]
    message_html: Optional[str]
    repository: Optional[str]
    title: Optional[str]
    type: str
    url: Optional[str]
    github_user: GithubUser


class ChangelogListing(Model):
    builds: list[Build]
    search: ChangelogSearch
    streams: list[UpdateStream]


class MultiplayerScores(Model):
    cursor: CursorT
    cursor_string: CursorStringT
    params: Any
    scores: list[MultiplayerScore]
    total: Optional[int]
    user_score: Optional[MultiplayerScore]


class MultiplayerScore(Model):
    id: int
    user_id: int
    room_id: int
    playlist_item_id: int
    beatmap_id: int
    rank: Grade
    total_score: int
    max_combo: int
    mods: list[Mod]
    statistics: Statistics
    passed: bool
    position: Optional[int]
    scores_around: Optional[MultiplayerScoresAround]
    user: User
    solo_score_id: int
    classic_total_score: int
    preserve: bool
    processed: bool
    ranked: bool
    maximum_statistics: Statistics
    total_score_without_mods: int
    best_id: Optional[int]
    type: str
    accuracy: float
    build_id: int
    ended_at: Datetime
    is_perfect_combo: bool
    replay: bool
    pp: float
    started_at: Datetime
    ruleset_id: int
    current_user_attributes: Any
    has_replay: bool
    legacy_perfect: bool
    legacy_score_id: Optional[int]
    legacy_total_score: int

    def beatmap(self):
        return self._fk_beatmap(self.beatmap_id)


class MultiplayerScoresAround(Model):
    higher: list[MultiplayerScore]
    lower: list[MultiplayerScore]


class NewsListing(Model):
    cursor: CursorT
    cursor_string: CursorStringT
    news_posts: list[NewsPost]
    news_sidebar: NewsSidebar
    search: NewsSearch


class NewsPost(Model):
    author: str
    edit_url: str
    first_image: Optional[str]
    first_image_2x: Field(name="first_image@2x", type=Optional[str])
    id: int
    published_at: Datetime
    slug: str
    title: str
    updated_at: Datetime
    content: Optional[str]
    navigation: Optional[NewsNavigation]
    preview: Optional[str]


class NewsNavigation(Model):
    newer: Optional[NewsPost]
    older: Optional[NewsPost]


class NewsSidebar(Model):
    current_year: int
    news_posts: list[NewsPost]
    years: list[int]


class SeasonalBackgrounds(Model):
    ends_at: Datetime
    backgrounds: list[SeasonalBackground]


class SeasonalBackground(Model):
    url: str
    user: UserCompact


class DifficultyAttributes(Model):
    attributes: BeatmapDifficultyAttributes


class BeatmapDifficultyAttributes(Model):
    max_combo: int
    star_rating: float

    # osu attributes
    aim_difficulty: Optional[float]
    approach_rate: Optional[float]
    flashlight_difficulty: Optional[float]
    overall_difficulty: Optional[float]
    slider_factor: Optional[float]
    speed_difficulty: Optional[float]
    speed_note_count: Optional[float]
    aim_difficult_slider_count: Optional[float]
    aim_difficult_strain_count: Optional[float]
    speed_difficult_strain_count: Optional[float]

    # taiko attributes
    stamina_difficulty: Optional[float]
    rhythm_difficulty: Optional[float]
    colour_difficulty: Optional[float]
    approach_rate: Optional[float]
    great_hit_window: Optional[float]

    # ctb attributes
    approach_rate: Optional[float]

    # mania attributes
    great_hit_window: Optional[float]
    score_multiplier: Optional[float]


class Events(Model):
    cursor: CursorT
    cursor_string: CursorStringT
    events: Field(type=list[_Event])


class BeatmapPack(Model):
    author: str
    date: Datetime
    name: str
    no_diff_reduction: bool
    # marked as nonnull on docs
    ruleset_id: Optional[int]
    tag: str
    url: str

    # optional attributes
    beatmapsets: Optional[list[Beatmapset]]
    user_completion_data: Optional[BeatmapPackUserCompletionData]


class Scores(Model):
    cursor: CursorT
    cursor_string: CursorStringT
    scores: list[Score]


# ================
# Parameter Models
# ================

# models which aren't used for serialization, but passed to OssapiV2 methods.


@dataclass
class ForumPoll:
    options: list[str]
    title: str

    # default values taken from https://osu.ppy.sh/docs/index.html#create-topic
    hide_results: bool = False
    length_days: int = 0
    max_options: int = 1
    vote_change: bool = False


# ===================
# Undocumented Models
# ===================


class BeatmapsetSearchResult(Model):
    beatmapsets: list[Beatmapset]
    cursor: CursorT
    recommended_difficulty: Optional[float]
    error: Optional[str]
    total: int
    search: Any
    cursor_string: Optional[str]


class BeatmapsetDiscussions(Model):
    beatmaps: list[Beatmap]
    cursor: CursorT
    discussions: list[BeatmapsetDiscussion]
    included_discussions: list[BeatmapsetDiscussion]
    reviews_config: ReviewsConfig
    users: list[UserCompact]
    cursor_string: Optional[str]
    beatmapsets: list[Beatmapset]


class BeatmapsetDiscussionReview(Model):
    # https://github.com/ppy/osu-web/blob/master/app/Libraries/BeatmapsetDis
    # cussionReview.php
    max_blocks: int


class BeatmapsetDiscussionPosts(Model):
    beatmapsets: list[BeatmapsetCompact]
    discussions: list[BeatmapsetDiscussion]
    cursor: CursorT
    posts: list[BeatmapsetDiscussionPost]
    users: list[UserCompact]
    cursor_string: Optional[str]


class BeatmapsetDiscussionVotes(Model):
    cursor: CursorT
    discussions: list[BeatmapsetDiscussion]
    votes: list[BeatmapsetDiscussionVote]
    users: list[UserCompact]
    cursor_string: Optional[str]


class BeatmapsetEventComment(Model):
    beatmap_discussion_id: int
    beatmap_discussion_post_id: int


class BeatmapsetEventCommentNoPost(Model):
    beatmap_discussion_id: int
    beatmap_discussion_post_id: Optional[int]


class BeatmapsetEventCommentNone(Model):
    beatmap_discussion_id: Optional[int]
    beatmap_discussion_post_id: Optional[int]


class BeatmapsetEventCommentChange(Generic[S], BeatmapsetEventCommentNone):
    old: S
    new: S


class BeatmapsetEventCommentLovedRemoval(BeatmapsetEventCommentNone):
    reason: str


class BeatmapsetEventCommentKudosuChange(BeatmapsetEventCommentNoPost):
    new_vote: KudosuVote
    votes: list[KudosuVote]


class BeatmapsetEventCommentKudosuRecalculate(BeatmapsetEventCommentNoPost):
    new_vote: Optional[KudosuVote]


class BeatmapsetEventCommentOwnerChange(BeatmapsetEventCommentNone):
    beatmap_id: int
    beatmap_version: str
    new_user_id: int
    new_user_username: str
    new_users: list[int]


class BeatmapsetEventCommentNominate(Model):
    # for some reason this comment type doesn't have the normal
    # beatmap_discussion_id and beatmap_discussion_post_id attributes (they're
    # not even null, just missing).
    modes: list[GameMode]


class BeatmapsetEventCommentWithNominators(BeatmapsetEventCommentNoPost):
    beatmap_ids: Optional[list[int]]
    nominator_ids: Optional[list[int]]


class BeatmapsetEventCommentWithSourceUser(BeatmapsetEventCommentNoPost):
    source_user_id: int
    source_user_username: str


class BeatmapsetEvent(Model):
    # https://github.com/ppy/osu-web/blob/master/app/Models/BeatmapsetEvent.php
    #
    # https://github.com/ppy/osu-web/blob/master/app/Transformers/BeatmapsetEv
    # entTransformer.php

    id: int
    type: BeatmapsetEventType
    comment: Any
    created_at: Datetime

    user_id: Optional[int]
    beatmapset: Optional[BeatmapsetCompact]
    discussion: Optional[BeatmapsetDiscussion]

    @staticmethod
    def override_attributes(data, api):
        mapping = {
            BeatmapsetEventType.BEATMAP_OWNER_CHANGE: BeatmapsetEventCommentOwnerChange,
            BeatmapsetEventType.DISCUSSION_DELETE: BeatmapsetEventCommentNoPost,
            # `api.beatmapset_events(types=[BeatmapsetEventType.DISCUSSION_LOCK])`
            # doesn't seem to be recognized, just returns all events. Was this
            # type discontinued?
            # BeatmapsetEventType.DISCUSSION_LOCK: BeatmapsetEventComment,
            BeatmapsetEventType.DISCUSSION_POST_DELETE: BeatmapsetEventComment,
            BeatmapsetEventType.DISCUSSION_POST_RESTORE: BeatmapsetEventComment,
            BeatmapsetEventType.DISCUSSION_RESTORE: BeatmapsetEventCommentNoPost,
            # same here
            # BeatmapsetEventType.DISCUSSION_UNLOCK: BeatmapsetEventComment,
            # Some events have a comment that is *just a string*.
            #   api.beatmapset_events(beatmapset_id=724033)
            # I've only seen this for "type": "disqualify", but who knows where
            # else it could happen. I've preemptively marked NOMINATION_RESET as
            # taking a string also.
            BeatmapsetEventType.DISQUALIFY: Union[
                BeatmapsetEventCommentWithNominators, str
            ],
            # same here
            # BeatmapsetEventType.DISQUALIFY_LEGACY: BeatmapsetEventComment
            BeatmapsetEventType.GENRE_EDIT: BeatmapsetEventCommentChange[str],
            BeatmapsetEventType.ISSUE_REOPEN: BeatmapsetEventComment,
            BeatmapsetEventType.ISSUE_RESOLVE: BeatmapsetEventComment,
            BeatmapsetEventType.KUDOSU_ALLOW: BeatmapsetEventCommentNoPost,
            BeatmapsetEventType.KUDOSU_DENY: BeatmapsetEventCommentNoPost,
            BeatmapsetEventType.KUDOSU_GAIN: BeatmapsetEventCommentKudosuChange,
            BeatmapsetEventType.KUDOSU_LOST: BeatmapsetEventCommentKudosuChange,
            BeatmapsetEventType.KUDOSU_RECALCULATE: BeatmapsetEventCommentKudosuRecalculate,
            BeatmapsetEventType.LANGUAGE_EDIT: BeatmapsetEventCommentChange[str],
            BeatmapsetEventType.LOVE: type(None),
            BeatmapsetEventType.NOMINATE: BeatmapsetEventCommentNominate,
            # same here
            # BeatmapsetEventType.NOMINATE_MODES: BeatmapsetEventComment,
            BeatmapsetEventType.NOMINATION_RESET: Union[
                BeatmapsetEventCommentWithNominators, str
            ],
            BeatmapsetEventType.NOMINATION_RESET_RECEIVED: BeatmapsetEventCommentWithSourceUser,
            BeatmapsetEventType.QUALIFY: type(None),
            BeatmapsetEventType.RANK: type(None),
            BeatmapsetEventType.REMOVE_FROM_LOVED: BeatmapsetEventCommentLovedRemoval,
            BeatmapsetEventType.NSFW_TOGGLE: BeatmapsetEventCommentChange[bool],
        }
        type_ = BeatmapsetEventType(data["type"])
        # some events don't seem to have an associate comment, eg
        #   api.beatmapset_events(beatmapset_id=692322)
        # I don't know under what circumstances this does or does not happen, so
        # I am marking all comments as optional.
        return {"comment": Optional[mapping[type_]]}

    def user(self) -> Optional[User]:
        return self._fk_user(self.user_id)


class ChatChannel(Model):
    channel_id: int
    description: Optional[str]
    icon: Optional[str]
    moderated: Optional[bool]
    name: str
    type: ChannelType
    uuid: Optional[str]
    message_length_limit: int

    # optional fields
    # ---------------
    last_message_id: Optional[int]
    last_read_id: Optional[int]
    recent_messages: Optional[list[ChatMessage]]
    users: Optional[list[int]]


class ChatMessage(Model):
    channel_id: int
    content: str
    is_action: bool
    message_id: int
    sender: UserCompact
    sender_id: int
    timestamp: Datetime
    # TODO enumify, example value: "plain"
    type: str


class CountryStatistics(Model):
    code: str
    active_users: int
    play_count: int
    ranked_score: int
    performance: int
    country: Country


class CreatePMResponse(Model):
    message: ChatMessage
    new_channel_id: int

    # undocumented
    channel: ChatChannel

    # documented but not present in response
    presence: Optional[list[ChatChannel]]


class ModdingHistoryEventsBundle(Model):
    # https://github.com/ppy/osu-web/blob/master/app/Libraries/ModdingHistor
    # yEventsBundle.php#L84
    events: list[BeatmapsetEvent]
    reviewsConfig: BeatmapsetDiscussionReview
    users: list[UserCompact]


class UserRelation(Model):
    # undocumented (and not a class on osu-web)
    # https://github.com/ppy/osu-web/blob/master/app/Transformers/UserRelatio
    # nTransformer.php#L16
    target_id: int
    relation_type: UserRelationType
    mutual: bool

    # optional fields
    # ---------------
    target: Optional[UserCompact]

    def target(self) -> Union[User, UserCompact]:
        return self._fk_user(self.target_id, existing=self.target)


class StatisticsVariant(Model):
    mode: GameMode
    variant: Variant
    country_rank: Optional[int]
    global_rank: Optional[int]
    pp: float


class UserStatistics(Model):
    count_100: int
    count_300: int
    count_50: int
    count_miss: int
    country_rank: Optional[int]
    grade_counts: UserGradeCounts
    hit_accuracy: float
    is_ranked: bool
    level: UserLevel
    maximum_combo: int
    play_count: int
    play_time: Optional[int]
    pp: Optional[float]
    pp_exp: float
    global_rank: Optional[int]
    global_rank_exp: Optional[float]
    # deprecated, replaced by global_rank and country_rank
    rank: Optional[Any]
    ranked_score: int
    rank_change_since_30_days: Optional[int]
    replays_watched_by_others: int
    total_hits: int
    total_score: int
    user: Optional[UserCompact]
    variants: Optional[list[StatisticsVariant]]


class UserStatisticsRulesets(Model):
    # undocumented
    # https://github.com/ppy/osu-web/blob/master/app/Transformers/UserStatisti
    # csRulesetsTransformer.php
    osu: Optional[UserStatistics]
    taiko: Optional[UserStatistics]
    fruits: Optional[UserStatistics]
    mania: Optional[UserStatistics]


class RoomPlaylistItemMod(Model):
    acronym: str
    settings: dict[str, Any]


class RoomPlaylistItem(Model):
    id: int
    room_id: int
    beatmap_id: int
    ruleset_id: int
    allowed_mods: list[RoomPlaylistItemMod]
    required_mods: list[RoomPlaylistItemMod]
    expired: bool
    owner_id: int
    # null for playlist items which haven't finished yet, I think
    playlist_order: Optional[int]
    # null for playlist items which haven't finished yet, I think
    played_at: Optional[Datetime]
    beatmap: BeatmapCompact


class _Room1(Model):
    id: int
    name: str
    category: RoomCategory
    type: RoomType
    user_id: int
    starts_at: Datetime
    ends_at: Optional[Datetime]
    max_attempts: Optional[int]
    participant_count: int
    channel_id: int
    active: bool
    has_password: bool
    queue_mode: str
    auto_skip: bool
    host: UserCompact
    playlist: list[RoomPlaylistItem]
    recent_participants: list[UserCompact]


class Room(Model):
    id: int
    name: str
    category: RoomCategory
    type: RoomType
    user_id: int
    starts_at: Datetime
    ends_at: Optional[Datetime]
    max_attempts: Optional[int]
    participant_count: int
    channel_id: int
    active: bool
    has_password: bool
    queue_mode: str
    auto_skip: bool
    host: UserCompact
    playlist: list[RoomPlaylistItem]

    # new from _Room1
    playlist_item_stats: RoomPlaylistItemStats
    current_playlist_item: Optional[RoomPlaylistItem]
    difficulty_range: RoomDifficultyRange
    recent_participants: list[UserCompact]

    @staticmethod
    def override_attributes(data, api):
        if api.api_version < 20220217:
            return _Room1


class RoomLeaderboardScore(Model):
    accuracy: float
    attempts: int
    completed: int
    pp: float
    room_id: int
    total_score: int
    user_id: int
    user: UserCompact


class RoomLeaderboardUserScore(RoomLeaderboardScore):
    position: int


class RoomLeaderboard(Model):
    leaderboard: list[RoomLeaderboardScore]
    user_score: Optional[RoomLeaderboardUserScore]


class Match(Model):
    id: int
    start_time: Datetime
    # null for matches which haven't finished yet, I think
    end_time: Optional[Datetime]
    name: str


class Matches(Model):
    matches: list[Match]
    cursor: CursorT
    params: Any
    cursor_string: CursorStringT


class MatchGame(Model):
    id: int
    start_time: Datetime
    # null for in-progress matches.
    end_time: Optional[Datetime]
    mode: GameMode
    mode_int: int
    scoring_type: ScoringType
    team_type: TeamType
    mods: list[Mod]
    # null for deleted beatmaps,
    # e.g. https://osu.ppy.sh/community/matches/103721175.
    # TODO doesn't match docs
    beatmap: Optional[BeatmapCompact]
    beatmap_id: int
    scores: list[Score]


class MatchEventDetail(Model):
    type: MatchEventType
    # seems to only be used for MatchEventType.OTHER
    text: Optional[str]


class MatchEvent(Model):
    id: int
    detail: MatchEventDetail
    timestamp: Datetime
    # can be none for MatchEventType.OTHER
    user_id: Optional[int]
    game: Optional[MatchGame]


class MatchResponse(Model):
    match: Match
    events: list[MatchEvent]
    users: list[UserCompact]
    first_event_id: int
    latest_event_id: int
    current_game_id: Optional[int]


class DailyChallengeUserStats(Model):
    daily_streak_best: int
    daily_streak_current: int
    last_update: Datetime
    last_weekly_streak: Datetime
    playcount: int
    top_10p_placements: int
    top_50p_placements: int
    user_id: int
    weekly_streak_best: int
    weekly_streak_current: int


class NonLegacyMod(Model):
    acronym: str
    settings: Any


class Tag(Model):
    id: int
    name: str
    description: str
    ruleset_id: Optional[int]


class Tags(Model):
    tags: list[Tag]


class BeatmapsPassed(Model):
    beatmaps_passed: list[BeatmapCompact]
