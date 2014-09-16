import requests
import re

section_title_re = re.compile('(?<===).*(?===)')
series_section_re = re.compile('.*(Series\s[A-Z][^=]*)')
episode_title_re = re.compile('(?<=\|Title=)([^<])*')
guests_cell_re = re.compile('(?<=\|Aux1=)(.)*')

params = {
    'format': 'json',
    'action': 'query',
    'prop': 'revisions',
    'rvprop': 'content',
    'titles': 'List_of_QI_episodes'
}
qi = {'series': {}}


def fetch_qi():
    r = requests.get('http://en.wikipedia.org/w/api.php', params=params)
    j = r.json()
    page = list(j['query']['pages'].values())[0]
    content = page['revisions'][0]['*']

    lines = content.split('\n')
    print('Fetched', len(lines), 'lines of content')

    current_series = ''
    num_series = 1
    num_episode = 1
    for line in lines:
        is_section = section_title_re.search(line)

        if is_section:
            current_series = is_section.group(0)

            is_series = series_section_re.search(line)
            if is_series:
                current_series = current_series
                se = {'name': current_series,
                      'number': num_series,
                      'episodes': list()}
                qi['series'][current_series] = se

                num_episode = 1
                num_series += 1
            else:
                current_series = ''
        elif current_series != '':
            is_episode = episode_title_re.search(line)
            is_guests = guests_cell_re.search(line)

            if is_episode:
                ep = {'name': is_episode.group(0),
                      'number': num_episode,
                      'guests': list()}
                qi['series'][current_series]['episodes'].append(ep)
                num_episode += 1

            elif is_guests:
                guests = is_guests.group(0).split('<br />')
                for g in guests:
                    g = re.sub('\[\[', '', g)
                    g = re.sub('\]\]', '', g)
                    qi['series'][current_series]['episodes'][num_episode-2]['guests'].append(g)


def list_episodes(s):
    series = sorted(qi['series'].items(), key=lambda x: x[1]['number'])[int(s)-1]
    headline = '\n' + str(series[1]['number']) + ' ' + series[1]['name'] + ' episodes'
    print(headline)
    print('='*len(headline))

    for episode in series[1]['episodes']:
        episode_title = str(episode['number']) + ' ' + episode['name'] + ':'
        print(episode_title, ', '.join(episode['guests']))
    print()


def list_seasons():
    headline = '\nQI Seasons'
    print(headline)
    print('='*len(headline))

    for series in sorted(qi['series'].items(), key=lambda x: x[1]['number']):
        headline = str(series[1]['number']) + ' ' + series[1]['name']
        print(headline)
    print()


def list_guests():
    headline = '\nQI Guests'
    print(headline)
    print('='*len(headline))

    seen_guests = set()
    for series in sorted(qi['series'].items(), key=lambda x: x[1]['number']):
        for episode in series[1]['episodes']:
            for guest in episode['guests']:
                if guest not in seen_guests:
                    print(guest)
                seen_guests.add(guest)
    print()


def menu_qi():
    while True:
        print('\n.###### MENU ######.')
        print('s - List QI seasons')
        print('e - List Episodes')
        print('g - List QI guests')
        print('q - Quit')
        print('.##################.')

        choice = input('>:')
        if choice == 'q':
            break
        elif choice == 's':
            list_seasons()
        elif choice == 'e':
            list_seasons()
            choice = input('List season:')
            list_episodes(choice)
        elif choice == 'g':
            list_guests()
        else:
            print('Unknown selection:', choice)


fetch_qi()
menu_qi()