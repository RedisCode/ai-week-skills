# UI And Routing

## Route conventions

Basecamp uses App Router with clear grouping by purpose.

- top-level app surfaces live under `app/`
- tool pages live under `app/tools/<slug>/`
- API handlers live under `app/api/.../route.ts`
- feature logic usually lives under `components/<feature>` and `lib/<feature>`
- admin surfaces live under `app/admin/...` when needed

For a new tool, start with this default tree:

```text
app/
  tools/
    <slug>/
      page.tsx
      layout.tsx        # optional
  api/
    <slug>/
      route.ts
components/
  <feature>/
    ...
lib/
  <feature>/
    ...
```

If the feature has history or rerunnable work, add:

```text
app/
  tools/
    <slug>/
      runs/
        page.tsx
        [id]/
          page.tsx
```

## Tool page shell

A typical Basecamp tool page is visually simple and structurally consistent:

- full-height dark background
- container with `px-4 py-8`
- back link to the tool index
- icon tile
- title and short description
- one main feature component beneath the header

The route component is usually thin. Example shape:

```tsx
export default function ToolPage() {
  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        <ToolHeader />
        <FeatureComponent />
      </div>
    </div>
  )
}
```

## Navigation registration

The source app keeps tool metadata in a shared registry. Each tool needs:

- numeric or otherwise stable ID
- clear name
- short description
- category
- icon
- URL
- optional featured or disabled state

The real lesson is that navigation is data-driven. New tools should be registered in one place and then consumed by role pages, dropdowns, and home cards.

## Role placement

Every tool should belong to a role bucket and usually to a smaller section within that role. Avoid "miscellaneous tool" placement unless forced.

Questions to answer:

- Is this for marketers, pipeline generators, or operators?
- Is it strategy, content, operations, AI, or another internal category?
- Should it appear on the home page teasers?
- Is it visible now, hidden, or teaser-only?

## Runtime configurability

The source app supports Redis-backed tool visibility overrides and custom ordering. Even if you do not reproduce that exact implementation in a new app, keep these capabilities in mind:

- hide a tool without redeploying
- mark a tool as teaser-only
- reorder tools by role

This is valuable for internal launches and phased rollouts.

## UI system

The source app uses a dark Redis-aligned brand theme:

- dark teal backgrounds
- white foreground text
- bright yellow primary accent
- red "hyper" accent for links and urgent actions
- Space Grotesk, Space Mono, Source Serif, and a branded display face

Do not default to generic light dashboards if the request is "make this fit Basecamp."

## Interaction patterns worth copying

- Required integration modal before using a dependent tool
- recent runs or recent history lists for repeatable workflows
- explicit loading, empty, and error states
- admin entry point in the header when a user has elevated access
- external links clearly opened in new tabs

## Responsive behavior

The source app handles desktop and mobile navigation separately. New tools should likewise avoid desktop-only assumptions:

- forms should stack gracefully
- long tables should scroll or collapse
- dropdown-heavy interactions need mobile-safe alternatives

## Copy style

Use short, operational copy:

- say what the tool does
- name the external system if relevant
- avoid consumer-marketing hype
- use verbs like create, clean, export, sync, connect, monitor

## Basecamp-compatible page checklist

- header follows the common pattern
- route name is action-oriented and readable
- tool has a role assignment
- integration dependencies are surfaced early
- empty, loading, and error states are intentional
- page works on mobile widths
