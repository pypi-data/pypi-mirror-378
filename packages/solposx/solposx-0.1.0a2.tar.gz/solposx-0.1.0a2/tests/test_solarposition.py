import pandas as pd
import numpy as np
import pytest
from solposx.solarposition import iqbal
from solposx.solarposition import michalsky
from solposx.solarposition import nasa_horizons
from solposx.solarposition import noaa
from solposx.solarposition import psa
from solposx.solarposition import sg2
from solposx.solarposition import sg2_c
from solposx.solarposition import skyfield
from solposx.solarposition import spa
from solposx.solarposition import usno
from solposx.solarposition import walraven


psa_2020_coefficients = [
    2.267127827, -9.300339267e-4, 4.895036035, 1.720279602e-2,
    6.239468336, 1.720200135e-2, 3.338320972e-2, 3.497596876e-4,
    -1.544353226e-4, -8.689729360e-6, 4.090904909e-1, -6.213605399e-9,
    4.418094944e-5, 6.697096103, 6.570984737e-2,
]


def expected_iqbal():
    columns = ['elevation', 'zenith', 'azimuth']
    values = [
        [32.3933559, 57.6066441, 205.057264],
        [32.3808669, 57.6191331, 205.103653],
        [35.10239415, 54.89760585, 169.4252099],
        [18.79386827, 71.20613173, 234.3799454],
        [35.58304355, 54.41695645, 197.47158811],
        [-9.32664685, 99.32664685, 201.24829056],
        [66.88194467, 23.11805533, 245.62133739],
        [9.32664685, 80.67335315, 338.75170944],
        [49.89989703, 40.10010297, 326.27538784],
        [35.56795719, 54.43204281, 175.44720266],
        [-53.03010805, 143.03010805, 18.66654047],
        [-53.03010805, 143.03010805, 18.66654047],
        [32.7577876, 57.2422124, 205.13681576],
        [32.7577876, 57.2422124, 205.13681576],
        [-23.30557846, 113.30557846, 79.558556],
        [1.23252489, 88.76747511, 104.52245037],
        [32.3933559, 57.6066441, 205.057264],
        [32.3933559, 57.6066441, 205.057264],
        [32.3933559, 57.6066441, 205.057264],
    ]
    data = pd.DataFrame(data=values, columns=columns)
    return data


def expected_michalsky_original_julian():
    columns = ['elevation', 'apparent_elevation', 'zenith', 'apparent_zenith',
               'azimuth']
    values = [
        [32.21780263, 32.24498279, 57.78219737, 57.75501721, 204.91751387],
        [32.20533693, 32.23252757, 57.79466307, 57.76747243, 204.96379895],
        [34.92279261, 34.9478766, 55.07720739, 55.0521234, 169.37618059],
        [18.63629794, 18.68330498, 71.36370206, 71.31669502, 234.18898285],
        [35.75816111, 35.78266275, 54.24183889, 54.21733725, 197.6747502],
        [-9.52972383, -8.96972383, 99.52972383, 98.96972383, 201.18805829],
        [66.85774447, 66.87103396, 23.14225553, 23.12896604, 245.08622522],
        [9.52972383,  9.62043934, 80.47027617, 80.37956066, 338.81194171],
        [50.10984044, 50.1274089, 39.89015956, 39.8725911, 326.23438218],
        [35.36181097, 35.38658543, 54.63818903, 54.61341457, 175.38864631],
        [-53.24139895, -52.68139895, 143.24139895, 142.68139895, 18.64775639],
        [-53.24139895, -52.68139895, 143.24139895, 142.68139895, 18.64775639],
        [33.19773834, 33.2241191, 56.80226166, 56.7758809, 205.09146059],
        [32.08343676, 32.11073039, 57.91656324, 57.88926961, 204.90619448],
        [-23.40757803, -22.84757803, 113.40757803, 112.84757803, 79.54939414],
        [1.10847034, 1.49128689, 88.89152966, 88.50871311, 104.54053775],
        [32.21780263, 32.24498279, 57.78219737, 57.75501721, 204.91751387],
        [32.21780263, 32.24498279, 57.78219737, 57.75501721, 204.91751387],
        [32.21780263, 32.24498279, 57.78219737, 57.75501721, 204.91751387],
    ]
    data = pd.DataFrame(data=values, columns=columns)
    return data


def expected_michalsky_pandas_julian():
    columns = ['elevation', 'apparent_elevation', 'zenith', 'apparent_zenith',
               'azimuth']
    values = [
        [32.21780263, 32.24498279, 57.78219737, 57.75501721, 204.91751387],
        [32.20533693, 32.23252757, 57.79466307, 57.76747243, 204.96379895],
        [34.92279261, 34.9478766,  55.07720739, 55.0521234,  169.37618059],
        [18.63629794, 18.68330498, 71.36370206, 71.31669502, 234.18898285],
        [35.75816111, 35.78266275, 54.24183889, 54.21733725, 197.6747502],
        [-9.52972383, -8.96972383, 99.52972383, 98.96972383, 201.18805829],
        [66.85774447, 66.87103396, 23.14225553, 23.12896604, 245.08622522],
        [9.52972383,  9.62043934,  80.47027617, 80.37956066, 338.81194171],
        [50.10984044, 50.1274089,  39.89015956, 39.8725911,  326.23438218],
        [35.36181097, 35.38658543, 54.63818903, 54.61341457, 175.38864631],
        [-53.24139895, -52.68139895, 143.24139895, 142.68139895, 18.64775639],
        [-53.24139895, -52.68139895, 143.24139895, 142.68139895, 18.64775639],
        [32.46357112, 32.49054619, 57.53642888, 57.50945381, 204.94138737],
        [32.44484719, 32.47183777, 57.55515281, 57.52816223, 204.97918825],
        [-23.40757803, -22.84757803, 113.40757803, 112.84757803, 79.54939414],
        [1.10847034,  1.49128689,  88.89152966, 88.50871311, 104.54053775],
        [32.21780263, 32.24498279, 57.78219737, 57.75501721, 204.91751387],
        [32.21780263, 32.24498279, 57.78219737, 57.75501721, 204.91751387],
        [32.21780263, 32.24498279, 57.78219737, 57.75501721, 204.91751387],
    ]
    data = pd.DataFrame(data=values, columns=columns)
    return data


def expected_michalsky_spencer_false():
    columns = ['elevation', 'apparent_elevation', 'zenith', 'apparent_zenith',
               'azimuth']
    values = [
        [32.21780263, 32.24498279, 57.78219737, 57.75501721, 204.91751387],
        [32.20533693, 32.23252757, 57.79466307, 57.76747243, 204.96379895],
        [34.92279261, 34.94787660, 55.07720739, 55.0521234, 169.37618059],
        [18.63629794, 18.68330498, 71.36370206, 71.31669502, 234.18898285],
        [35.75816111, 35.78266275, 54.24183889, 54.21733725, 197.67475020],
        [-9.52972383, -8.96972383, 99.52972383, 98.96972383, 201.18805829],
        [66.85774447, 66.87103396, 23.14225553, 23.12896604, 294.91377478],
        [9.52972383,  9.62043934, 80.47027617, 80.37956066, 201.18805829],
        [50.10984044, 50.1274089, 39.89015956, 39.8725911, 213.76561782],
        [35.36181097, 35.38658543, 54.63818903, 54.61341457, 175.38864631],
        [-53.24139895, -52.68139895, 143.24139895, 142.68139895, 18.64775639],
        [-53.24139895, -52.68139895, 143.24139895, 142.68139895, 18.64775639],
        [33.19773834, 33.2241191, 56.80226166, 56.7758809, 205.09146059],
        [32.08343676, 32.11073039, 57.91656324, 57.88926961, 204.90619448],
        [-23.40757803, -22.84757803, 113.40757803, 112.84757803, 79.54939414],
        [1.10847034, 1.49128689, 88.89152966, 88.50871311, 104.54053775],
        [32.21780263, 32.24498279, 57.78219737, 57.75501721, 204.91751387],
        [32.21780263, 32.24498279, 57.78219737, 57.75501721, 204.91751387],
        [32.21780263, 32.24498279, 57.78219737, 57.75501721, 204.91751387],
    ]
    data = pd.DataFrame(data=values, columns=columns)
    return data


def expected_noaa():
    columns = ['elevation', 'apparent_elevation', 'zenith', 'apparent_zenith',
               'azimuth']
    values = [
        [32.21715174, 32.24268539, 57.78284826, 57.75731461, 204.92232395],
        [32.20468378, 32.23022967, 57.79531622, 57.76977033, 204.96860803],
        [34.92392895, 34.94698595, 55.07607105, 55.05301405, 169.38094302],
        [18.63438988, 18.68174893, 71.36561012, 71.31825107, 234.19290241],
        [35.75618186, 35.77854313, 54.24381814, 54.22145687, 197.67357003],
        [-9.52911395, -9.49473778, 99.52911395, 99.49473778, 201.19219097],
        [66.85423515, 66.8611327, 23.14576485, 23.1388673, 245.09172279],
        [9.52911581, 9.62132639, 80.47088419,  80.3786736, 338.80780907],
        [50.10765752, 50.12113671, 39.89234248, 39.87886329, 326.22893168],
        [35.36265374, 35.38534047, 54.63734626, 54.61465953, 175.39359304],
        [-53.23987161, -53.23556094, 143.23987161, 143.23556094, 18.65415239],
        [-53.23987161, -53.23556094, 143.23987161, 143.23556094, 18.65415239],
        [32.46248831, 32.48778263, 57.53751169, 57.51221737, 204.95376627],
        [32.44117331, 32.4664883, 57.55882669, 57.5335117, 204.97518601],
        [-23.40444445, -23.39111232, 113.40444445, 113.39111232, 79.55187937],
        [1.11161226, 1.46445929, 88.88838774, 88.53554071, 104.54291476],
        [32.21715174, 32.24268539, 57.78284826, 57.75731461, 204.92232395],
        [32.21715174, 32.24268539, 57.78284826, 57.75731461, 204.92232395],
        [32.21715174, 32.24268539, 57.78284826, 57.75731461, 204.92232395],
    ]
    data = pd.DataFrame(data=values, columns=columns)
    return data


def expected_psa_2001():
    columns = ['elevation', 'zenith', 'azimuth']
    values = [
        [32.21434385, 57.78565615, 204.91957868],
        [32.20187689, 57.79812311, 204.96586258],
        [34.92027644, 55.07972356, 169.3788305],
        [18.63211707, 71.36788293, 234.19028111],
        [35.75446859, 54.24553141, 197.67713395],
        [-9.53293173, 99.53293173, 201.19017401],
        [66.85455175, 23.14544825, 245.08643499],
        [9.52811892, 80.47188108, 338.80982599],
        [50.10817913, 39.89182087, 326.23090017],
        [35.35914111, 54.64085889, 175.39125721],
        [-53.24316093, 143.24316093, 18.65145716],
        [-53.24316093, 143.24316093, 18.65145716],
        [32.46428802, 57.53571198, 204.93415982],
        [32.43981197, 57.56018803, 204.98955089],
        [-23.40890746, 113.40890746, 79.55160745],
        [1.10690714, 88.89309286, 104.54258663],
        [32.21434385, 57.78565615, 204.91957868],
        [32.21434385, 57.78565615, 204.91957868],
        [32.21434385, 57.78565615, 204.91957868],
    ]
    data = pd.DataFrame(data=values, columns=columns)
    return data


def expected_psa_2020():
    columns = ['elevation', 'zenith', 'azimuth']
    values = [
        [32.21595946, 57.78404054, 204.9167547],
        [32.20349382, 57.79650618, 204.96304003],
        [34.92071906, 55.07928094, 169.37535422],
        [18.63439275, 71.36560725, 234.1884117],
        [35.7535716, 54.2464284, 197.67796274],
        [-9.5321134, 99.5321134, 201.18736969],
        [66.85741664, 23.14258336, 245.08558596],
        [9.52730057, 80.47269943, 338.81263031],
        [50.10853074, 39.89146926, 326.23536385],
        [35.35979872, 54.64020128, 175.38781378],
        [-53.24299848, 143.24299848, 18.64664538],
        [-53.24299848, 143.24299848, 18.64664538],
        [32.47215358, 57.52784642, 204.9305477],
        [32.43510874, 57.56489126, 204.98638231],
        [-23.41028925, 113.41028925, 79.54884709],
        [1.10556787, 88.89443213, 104.54003062],
        [32.21595946, 57.78404054, 204.9167547],
        [32.21595946, 57.78404054, 204.9167547],
        [32.21595946, 57.78404054, 204.9167547],
    ]
    data = pd.DataFrame(data=values, columns=columns)
    return data


def expected_sg2():
    # The expected values were generated using the official SG2 Python wrapper
    # and the SG2 SAE refraction correction
    columns = ['elevation', 'apparent_elevation', 'zenith', 'apparent_zenith',
               'azimuth']
    values = [
        [32.21696737, 32.24355729, 57.78303263, 57.75644271, 204.91857639],
        [32.2045009, 32.2311035, 57.7954991, 57.7688965, 204.96486201],
        [34.92230526, 34.94633034, 55.07769474, 55.05366966, 169.37656689],
        [18.63488143, 18.6838735, 71.36511857, 71.3161265, 234.19025564],
        [35.75666309, 35.77996471, 54.24333691, 54.22003529, 197.67009822],
        [-9.53068757, -9.49650419, 99.53068757, 99.49650419, 201.18854894],
        [66.85690391, 66.86409239, 23.14309609, 23.13590761, 245.09007204],
        [9.52588549, 9.61972777, 80.47411451, 80.38027223, 338.81145106],
        [50.10677054, 50.1208336, 39.89322946, 39.8791664, 326.23457619],
        [35.36128972, 35.38493054, 54.63871028, 54.61506946, 175.38913627],
        [-53.24134227, -53.23705528, 143.24134227, 143.23705528, 18.64798841],
        [-53.24134227, -53.23705528, 143.24134227, 143.23705528, 18.64798841],
        [np.nan, np.nan, np.nan, np.nan, np.nan],
        [np.nan, np.nan, np.nan, np.nan, np.nan],
        [-23.40828474, -23.39502759, 113.40828474, 113.39502759, 79.54872263],
        [1.10752265, 1.45828141, 88.89247735, 88.54171859, 104.53992596],
        [32.21696737, 32.24355729, 57.78303263, 57.75644271, 204.91857639],
        [32.2169674, 32.24355732, 57.7830326, 57.75644268, 204.91857639],
        [32.21696607, 32.24355599, 57.78303393, 57.75644401, 204.91857639],
    ]
    data = pd.DataFrame(data=values, columns=columns)
    return data


def expected_skyfield():
    columns = ['elevation', 'zenith', 'azimuth']
    values = [
        [32.21731177, 57.78268823, 204.91794786],
        [32.20484556, 57.79515444, 204.96423388],
        [34.92239511, 55.07760489, 169.37578931],
        [18.63535617, 71.36464383, 234.18984836],
        [35.75683037, 54.24316963, 197.66893877],
        [-9.5305175, 99.5305175, 201.18798691],
        [66.85755467, 23.14244533, 245.08983994],
        [9.52569869, 80.47430131, 338.81201317],
        [50.10684928, 39.89315072, 326.23556156],
        [35.36142589, 54.63857411, 175.38836795],
        [-53.24128453, 143.24128453, 18.64711844],
        [-53.24128453, 143.24128453, 18.64711844],
        [32.43211642, 57.56788358, 205.06175657],
        [32.62788726, 57.36871411, 204.26008339],
        [-23.40856284, 113.40856284, 79.54814898],
        [1.10723972, 88.89276028, 104.53937506],
        [32.21731177, 57.78268823, 204.91794786],
        [32.21731177, 57.78268823, 204.91794786],
        [32.21731177, 57.78268823, 204.91794786],
    ]
    data = pd.DataFrame(data=values, columns=columns)
    data['zenith'] = 90 - data['elevation']
    return data


def expected_spa():
    columns = ['elevation', 'apparent_elevation', 'zenith', 'apparent_zenith', 'azimuth',
               'equation_of_time']
    values = [
        [32.21708674, 32.24367654, 57.78291326, 57.75632346, 204.9188164, 14.75816027],
        [32.20462016, 32.23122263, 57.79537984, 57.76877737, 204.96510208, 14.75818295],
        [34.92249857, 34.94652348, 55.07750143, 55.05347652, 169.3767211, 14.74179647],
        [18.63493009, 18.68392203, 71.36506991, 71.31607797, 234.19049983, 14.77445424],
        [35.75662074, 35.77992239, 54.24337926, 54.22007761, 197.67009996, -12.4319873],
        [-9.53051391, -9.53051391, 99.53051391, 99.53051391, 201.18870641, 14.75816027],
        [66.85682918, 66.86401769, 23.14317082, 23.13598231, 245.09065324, 14.75816027],
        [9.52569499, 9.61953906, 80.47430501, 80.38046094, 338.81129359, 14.75816027],
        [50.10653615, 50.12059933, 39.89346385, 39.87940067, 326.23446721, 14.75816027],
        [35.36147343, 35.38511409, 54.63852657, 54.61488591, 175.38931352, 14.75816027],
        [-53.24113451, -53.24113451, 143.24113451, 143.24113451, 18.64817122, 14.75816027],
        [-53.24113451, -53.24113451, 143.24113451, 143.24113451, 18.64817122, 14.75816027],
        [32.4622024, 32.48854464, 57.5377976, 57.51145536, 204.94926574, 14.55795391],
        [32.4407131, 32.46707691, 57.5592869, 57.53292309, 204.96985758, 14.64779166],
        [-23.40808954, -23.40808954, 113.40808954, 113.40808954, 79.54868063, 14.68397497],
        [1.10773228, 1.45847482, 88.89226772, 88.54152518, 104.53989829, 14.70334338],
        [32.21708674, 32.24367654, 57.78291326, 57.75632346, 204.9188164, 14.75816027],
        [32.21708677, 32.24367657, 57.78291323, 57.75632343, 204.9188164, 14.75816027],
        [32.21708544, 32.24367524, 57.78291456, 57.75632476, 204.9188164, 14.75816027],
    ]
    data = pd.DataFrame(data=values, columns=columns)
    return data


def expected_usno():
    columns = ['elevation', 'zenith', 'azimuth']
    values = [
       [32.21913058, 57.78086942, 204.91396212],
       [32.20666654, 57.79333346, 204.9602485],
       [34.92271632, 55.07728368, 169.37217155],
       [18.63848631, 71.36151369, 234.18640074],
       [35.75823472, 54.24176528, 197.67107057],
       [-9.52936557, 99.52936557, 201.18474698],
       [66.86088833, 23.13911167, 245.08379957],
       [9.52936557,  80.47063443, 338.81525302],
       [50.11081313, 39.88918687, 326.23927513],
       [35.36198031, 54.63801969, 175.38462327],
       [-53.24179879, 143.24179879, 18.6423076],
       [-53.24179879, 143.24179879, 18.6423076],
       [32.46463884, 57.53536116, 204.9389006],
       [32.44304455, 57.55695545, 204.98724112],
       [-23.40963192, 113.40963192, 79.54658304],
       [1.10645791, 88.89354209, 104.53792899],
       [32.21913058, 57.78086942, 204.91396212],
       [32.21913058, 57.78086942, 204.91396212],
       [32.21913058, 57.78086942, 204.91396212],
    ]
    data = pd.DataFrame(data=values, columns=columns)
    return data


def expected_usno_option_2():
    columns = ['elevation', 'zenith', 'azimuth']
    values = [
        [32.21913452, 57.78086548, 204.91394742],
        [32.20667049, 57.79332951, 204.96023379],
        [34.92271497, 55.07728503, 169.37215926],
        [18.63849557, 71.36150443, 234.18638706],
        [35.7582376, 54.2417624, 197.67105461],
        [-9.52936557, 99.52936557, 201.18473375],
        [66.86090033, 23.13909967, 245.08378652],
        [9.52936557, 80.47063443, 338.81526625],
        [50.11081833, 39.88918167, 326.2392938],
        [35.36197956,  54.63802044, 175.38460729],
        [-53.24180178, 143.24180178, 18.64228637],
        [-53.24180178, 143.24180178, 18.64228637],
        [32.46465875, 57.53534125, 204.93882613],
        [32.44303542, 57.55696458, 204.98727521],
        [-23.40963198, 113.40963198, 79.54658298],
        [1.10645552, 88.89354448, 104.53792651],
        [32.21913452, 57.78086548, 204.91394742],
        [32.21913452, 57.78086548, 204.91394742],
        [32.21913452, 57.78086548, 204.91394742],
    ]
    data = pd.DataFrame(data=values, columns=columns)
    return data


def expected_walraven():
    columns = ['elevation', 'zenith', 'azimuth']
    values = [
        [32.21577184, 57.78422816, 204.9145408],
        [32.20330752, 57.79669248, 204.96082497],
        [34.91988403, 55.08011597, 169.37445826],
        [18.63514306, 71.36485694, 234.18579686],
        [35.75942569, 54.24057431, 197.67543014],
        [-9.53241956, 99.53241956, 201.18624892],
        [66.85832643, 23.14167357, 245.07813388],
        [9.53241956, 80.46758044, 338.81375108],
        [50.11302395, 39.88697605, 326.23525905],
        [35.35901685, 54.64098315, 175.38665251],
        [-53.24443195, 143.24443195, 18.64588668],
        [-53.24443195, 143.24443195, 18.64588668],
        [33.19945919, 56.80054081, 205.08690939],
        [32.078221, 57.921779, 204.90430273],
        [-23.41074972, 113.41074972, 79.55008786],
        [1.10528968, 88.89471032, 104.541125],
        [32.21577184, 57.78422816, 204.9145408],
        [32.21577184, 57.78422816, 204.9145408],
        [32.21577184, 57.78422816, 204.9145408],
    ]
    data = pd.DataFrame(data=values, columns=columns)
    return data


@pytest.fixture()
def test_conditions():
    inputs = pd.DataFrame(
        columns=['time', 'latitude', 'longitude', 'elevation'],
        data=(
            # Units: time, degrees, degrees, m
            ['2020-10-17T12:30+00:00', 45, 10, None],  # reference
            ['2020-10-17T12:30:10+00:00', 45, 10, None],  # non-zero seconds
            ['2020-10-17T12:30+02:00', 45, 10, None],  # positive timezone
            ['2020-10-17T12:30-02:00', 45, 10, None],  # negative timezone
            ['2020-02-29T12:30+00:00', 45, 10, None],  # leap day
            ['2020-10-17T12:30+00:00', 90, 10, None],  # 90 degree latitude
            ['2020-10-17T12:30+00:00', 0, 10, None],  # zero latitude
            ['2020-10-17T12:30+00:00', -90, 10, None],  # -90 degree latitude
            ['2020-10-17T12:30+00:00', -45, 10, None],  # negative mid-latitude
            ['2020-10-17T12:30+00:00', 45, -15, None],  # negative longitude
            ['2020-10-17T12:30+00:00', 45, -180, None],  # 180-degree longitude
            ['2020-10-17T12:30+00:00', 45, 180, None],  # 180-degree longitude
            ['1800-10-17T12:30+00:00', 45, 10, None],  # 200 years in the past
            ['2200-10-17T12:30+00:00', 45, 10, None],  # 200 years ahead
            ['2020-10-17T03:30+00:00', 45, 10, None],  # negative sun elevation
            ['2020-10-17T05:50+00:00', 45, 10, None],  # ~1-deg sun elevation
            ['2020-10-17T12:30+00:00', 45, 10, 0],  # zero altitude
            ['2020-10-17T12:30+00:00', 45, 10, -100],  # negative altitude
            ['2020-10-17T12:30+00:00', 45, 10, 4000],  # positive altitude
        ),
        dtype=object,  # avoids converting None to nan
    )
    inputs = inputs.set_index('time')
    inputs.index = [pd.Timestamp(ii) for ii in inputs.index]
    return inputs


def _generate_solarposition_dataframe(inputs, algorithm, **kwargs):
    """
    Generate DataFrame with solar positions.

    Each row is calculated separately due pd.DatetimeIndex being unable to
    handle multiple timezones.
    """
    dfs = []
    for index, row in inputs.iterrows():
        try:
            elevation_dict = {}
            if row['elevation'] is not None:
                if algorithm.__name__ in ['sg2', 'sg2_c', 'spa']:
                    elevation_dict['elevation'] = row['elevation']
            dfi = algorithm(
                pd.DatetimeIndex([index]),
                row['latitude'],
                row['longitude'],
                **{**kwargs, **elevation_dict},
            )
        except ValueError:
            # Add empty row (nans)
            dfi = pd.DataFrame(index=[index])
        dfs.append(dfi)
        df = pd.concat(dfs, axis='rows')
    return df


@pytest.mark.parametrize('algorithm,expected,kwargs', [
    (iqbal, expected_iqbal, {}),
    (michalsky, expected_michalsky_original_julian, {}),
    (michalsky, expected_michalsky_original_julian,
     {'spencer_correction': True, 'julian_date': 'original'}),
    (michalsky, expected_michalsky_pandas_julian,
     {'spencer_correction': True, 'julian_date': 'pandas'}),
    (michalsky, expected_michalsky_spencer_false,
     {'spencer_correction': False, 'julian_date': 'original'}),
    (noaa, expected_noaa, {}),
    (noaa, expected_noaa, {'delta_t': None}),
    (psa, expected_psa_2001, {'coefficients': 2001}),
    (psa, expected_psa_2020, {'coefficients': 2020}),
    # test custom psa coefficients
    (psa, expected_psa_2020, {'coefficients': psa_2020_coefficients}),
    (sg2, expected_sg2, {}),
    (sg2_c, expected_sg2, {}),
    (skyfield, expected_skyfield, {}),
    (spa, expected_spa, {}),
    (usno, expected_usno, {}),
    (usno, expected_usno, {'delta_t': None}),
    # test default usno gmst_option parameter
    (usno, expected_usno, {'gmst_option': 1}),
    (usno, expected_usno_option_2, {'gmst_option': 2}),
    (walraven, expected_walraven, {}),
])
def test_algorithm(algorithm, expected, kwargs, test_conditions):
    expected = expected().set_index(test_conditions.index)
    result = _generate_solarposition_dataframe(
        test_conditions, algorithm, **kwargs)
    result.name = algorithm.__module__

    pd.testing.assert_index_equal(expected.index, result.index)
    testing_kwargs = {'rtol': 1e-3} if algorithm.__name__ == 'sg2' else {'rtol': 1e-9}
    pd.testing.assert_frame_equal(
        expected, result, check_like=False, **testing_kwargs)
    for c in expected.columns:
        pd.testing.assert_series_equal(expected[c], result[c], **testing_kwargs)


def test_michalsky_julian_date_value_error():
    with pytest.raises(ValueError, match='julian_date` has to be either'):
        _ = michalsky(
            times=pd.date_range('2020-01-01', '2020-01-02', tz='UTC'),
            latitude=50, longitude=10,
            julian_date='wrong_option',
        )


def test_psa_coefficients_value_error():
    with pytest.raises(ValueError, match='unknown coefficients set: 1999'):
        _ = psa(
            times=pd.date_range('2020-01-01', '2020-01-02', tz='UTC'),
            latitude=50, longitude=10,
            coefficients=1999,  # not a correct option
        )
    with pytest.raises(ValueError, match='unknown coefficients set'):
        _ = psa(
            times=pd.date_range('2020-01-01', '2020-01-02', tz='UTC'),
            latitude=50, longitude=10,
            coefficients='not_an_option',  # not a correct option
        )


def test_usno_gmst_option_value_error():
    with pytest.raises(ValueError,
                       match='not a valid `gmst_option`'):
        _ = usno(
            times=pd.date_range('2020-01-01', '2020-01-02', tz='UTC'),
            latitude=50, longitude=10,
            gmst_option='not_an_option',
        )


def test_noaa_refraction_85_degrees():
    # Test that NOAA sets refraction to zero for solar
    # elevation angles between (85 and 90]
    # The below example has a solar elevation angle of 87.9
    angles = noaa(
        times=pd.date_range('2020-03-23 12', periods=1, tz='UTC'),
        latitude=0, longitude=0,
    )
    assert angles['elevation'].iloc[0] == angles['apparent_elevation'].iloc[0]


def test_delta_t_array_input():
    # test that delta_t can be specified as either an array or float
    times = pd.date_range('2020-03-23 12', periods=10, tz='UTC')
    delta_t = np.ones(len(times)) * 67.0
    # test noaa - array
    noaa_array = noaa(times, 50, 10, delta_t=delta_t)
    noaa_float = noaa(times, 50, 10, delta_t=67.0)
    pd.testing.assert_frame_equal(noaa_array, noaa_float)
    # test usno - array
    usno_array = usno(times, 50, 10, delta_t=delta_t)
    usno_float = usno(times, 50, 10, delta_t=67.0)
    pd.testing.assert_frame_equal(usno_array, usno_float)


def test_delta_t_series_input():
    # test that delta_t can be specified as either an array or float
    times = pd.date_range('2020-03-23 12', periods=10, tz='UTC')
    delta_t = np.ones(len(times)) * 67.0
    delta_t_series = pd.Series(delta_t, index=times)
    # test noaa - series
    noaa_array = noaa(times, 50, 10, delta_t=delta_t_series)
    noaa_float = noaa(times, 50, 10, delta_t=67.0)
    pd.testing.assert_frame_equal(noaa_array, noaa_float)
    # test usno - series
    usno_array = usno(times, 50, 10, delta_t=delta_t_series)
    usno_float = usno(times, 50, 10, delta_t=67.0)
    pd.testing.assert_frame_equal(usno_array, usno_float)


def expected_nasa():
    columns = ['right_ascension', 'declination', 'azimuth', 'elevation']
    values = [
        [280.88906, -23.05994, 18.384905, -62.107511],
        [280.93553, -23.05679, 43.990328, -57.075255],
        [280.98196, -23.05366, 63.159488, -49.306617],
        [281.02831, -23.05055, 77.862491, -40.227454],
        [281.07457, -23.04745, 90.093838, -30.655578],
        [281.12071, -23.04436, 101.147333, -21.076943],
        [281.16674, -23.04126, 111.849769, -11.846393],
        [281.21264, -23.03814, 122.773903, -3.289769],
        [281.25844, -23.03499, 134.336441, 4.244699],
        [281.30413, -23.03181, 146.804482, 10.367984],
        [281.34975, -23.02857, 160.234863, 14.670438],
        [281.39533, -23.02529, 174.399466, 16.791713],
        [281.44088, -23.02194, 188.799258, 16.525775],
        [281.48645, -23.01854, 202.838039, 13.899667],
        [281.53206, -23.01509, 216.06712, 9.162424],
        [281.57774, -23.01159, 228.325009, 2.693785],
        [281.62351, -23.00806, 239.722349, -5.096802],
        [281.66938, -23.00449, 250.562948, -13.828891],
        [281.71537, -23.0009, 261.295115, -23.161504],
        [281.76148, -22.99731, 272.536349, -32.767466],
        [281.80769, -22.99372, 285.194755, -42.273221],
        [281.854, -22.99014, 300.704397, -51.139645],
        [281.90038, -22.98658, 321.186284, -58.434214],
        [281.9468, -22.98304, 348.166418, -62.592241],
        [281.99323, -22.97954, 18.119982, -62.052919],
    ]
    data = pd.DataFrame(data=values, columns=columns)
    data.index = pd.date_range('2020-01-01', '2020-01-02', freq='1h', tz='UTC')
    data.index.name = 'time'
    data.index.freq = None
    return data


def test_nasa_horizons():
    expected = expected_nasa()

    result = nasa_horizons(
        latitude=50,
        longitude=10,
        start='2020-01-01',
        end='2020-01-02',
    )
    for c in expected.columns:
        pd.testing.assert_series_equal(expected[c], result[c])


def test_nasa_horizons_frequency_daily():
    start = '2020-01-01'
    end = '2020-01-03'
    result = nasa_horizons(
        latitude=50,
        longitude=10,
        start=start,
        end=end,
        time_step='1d',  # daily
    )
    expected_index = pd.date_range(start, end, freq='d', tz='UTC')
    expected_index.name = 'time'
    expected_index.freq = None

    pd.testing.assert_index_equal(expected_index, result.index)


def test_nasa_horizons_frequency_monthly():
    start = '2020-01-01'
    end = '2020-02-02'
    result = nasa_horizons(
        latitude=50,
        longitude=10,
        start=start,
        end=end,
        time_step='1mo',  # monthly
    )
    expected_index = pd.date_range(start, end, freq='MS', tz='UTC')
    expected_index.name = 'time'
    expected_index.freq = None

    pd.testing.assert_index_equal(expected_index, result.index)


def test_site_elevation_sg2():
    # Make sure that site elevations used by the SG2 algorithm
    # Due to the low tolerances for the other tests for this algorithm
    # This extra test is necessary
    times = pd.DatetimeIndex(['2020-01-01T12:00+02'])
    latitude, longitude = 50, 10
    zero_elevation = sg2(times, latitude, longitude, elevation=0)
    high_elevation = sg2(times, latitude, longitude, elevation=4000)
    none_elevation = sg2(times, latitude, longitude)
    assert zero_elevation.iloc[0]['elevation'] != high_elevation.iloc[0]['elevation']
    assert zero_elevation.iloc[0]['elevation'] == none_elevation.iloc[0]['elevation']
