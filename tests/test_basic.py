def test_import():
    import pyromsobs

def test_merge():
    import pyromsobs
    from numpy import array

    obs1 = pyromsobs.OBSstruct()
    obs1.value = array([5.])
    obs1.type = array([6])
    obs1.error = array([0.5])
    obs1.Xgrid = array([1.2])
    obs1.Ygrid = array([1.4])
    obs1.Zgrid = array([5.2])
    obs1.time =  array([15782.5])
    obs1 = pyromsobs.utils.setDimensions(obs1)

    obs2 = pyromsobs.OBSstruct()
    obs2.value = array([8.])
    obs2.type = array([6])
    obs2.error = array([0.5])
    obs2.Xgrid = array([1.6])
    obs2.Ygrid = array([1.8])
    obs2.Zgrid = array([5.4])
    obs2.time = array([15782.5])
    obs2 = pyromsobs.utils.setDimensions(obs2)

    obs3 = pyromsobs.OBSstruct()
    obs3.value = array([5., 8.])
    obs3.type = array([6, 6])
    obs3.error = array([0.5, 0.5])
    obs3.Xgrid = array([1.2, 1.6])
    obs3.Ygrid = array([1.4, 1.8])
    obs3.Zgrid = array([5.2, 5.4])
    obs3.time =  array([15782.5, 15782.5] )
    obs3 = pyromsobs.utils.setDimensions(obs3)

    obs4 = pyromsobs.merge([obs2, obs1])

    for var in ['value', 'error', 'Xgrid', 'Ygrid', 'Zgrid']:
        assert all(getattr(obs4, var) == getattr(obs3, var))



def test_superob():
    import pyromsobs
    from numpy import array

    obs1 = pyromsobs.OBSstruct()
    obs1.value = array([5.])
    obs1.type = array([6])
    obs1.error = array([0.5])
    obs1.Xgrid = array([1.2])
    obs1.Ygrid = array([1.4])
    obs1.Zgrid = array([5.2])
    obs1.time =  array([15782.5])
    obs1 = pyromsobs.utils.setDimensions(obs1)


    obs2 = pyromsobs.OBSstruct()
    obs2.value = array([8.])
    obs2.type = array([6])
    obs2.error = array([0.5])
    obs2.Xgrid = array([1.6])
    obs2.Ygrid = array([1.8])
    obs2.Zgrid = array([5.4])
    obs2.time = array([15782.5])
    obs2 = pyromsobs.utils.setDimensions(obs2)

    obs3 = pyromsobs.merge([obs2, obs1])

    obs3 = pyromsobs.superob(obs3)
    for var in ['value', 'error', 'Xgrid', 'Ygrid', 'Zgrid']:
        assert getattr(obs3, var) == (getattr(obs1, var) + getattr(obs2, var))/2.


def test_remove_duplicates():
    import pyromsobs
    from numpy import array

    obs1 = pyromsobs.OBSstruct()
    obs1.value = array([5.])
    obs1.type = array([6])
    obs1.error = array([0.5])
    obs1.Xgrid = array([1.2])
    obs1.Ygrid = array([1.4])
    obs1.Zgrid = array([5.2])
    obs1.time =  array([15782.5])
    obs1 = pyromsobs.utils.setDimensions(obs1)


    obs2 = pyromsobs.OBSstruct()
    obs2.value = array([5.])
    obs2.type = array([6])
    obs2.error = array([0.5])
    obs2.Xgrid = array([1.2])
    obs2.Ygrid = array([1.4])
    obs2.Zgrid = array([5.2])
    obs2.time = array([15782.5])
    obs2 = pyromsobs.utils.setDimensions(obs2)

    obs3 = pyromsobs.merge([obs2, obs1])

    obs3 = pyromsobs.remove_duplicates(obs3)
    assert obs3.Ndatum == 1
    for var in ['value', 'error', 'Xgrid', 'Ygrid', 'Zgrid']:
        assert getattr(obs3, var) == getattr(obs1, var)

def test_put():

    import pyromsobs
    from numpy import array, isin

    obs3 = pyromsobs.OBSstruct()
    obs3.value = array([5., 8.])
    obs3.type = array([6, 6])
    obs3.error = array([0.5, 0.5])
    obs3.Xgrid = array([1.2, 1.6])
    obs3.Ygrid = array([1.4, 1.8])
    obs3.Zgrid = array([5.2, 5.4])
    obs3.time =  array([15782.5, 15782.5] )
    obs3 = pyromsobs.utils.setDimensions(obs3)

    obs_dict = {'value': 6, 'type': 3, 'error': 0.4, 'Xgrid': 10, 'Ygrid': 15, 'Zgrid': 35.2, 'time': 15782.0, 'provenance': 10}
    obs = pyromsobs.OBSstruct()

    obs.put(obs_dict, fill_value = -99999)
    obs3.put(obs_dict, fill_value = -99999)

    assert obs3.Ndatum == 3
    assert any(isin(obs3.value, 6))
    assert any(isin(obs3.provenance, 10))
    assert any(isin(obs3.provenance, -99999))

    assert obs.Ndatum == 1
    assert obs.value == 6
    assert obs.provenance == 10

def test_index():

    import pyromsobs
    from numpy import array, isin, where

    obs3 = pyromsobs.OBSstruct()
    obs3.value = array([5., 8.])
    obs3.type = array([6, 6])
    obs3.error = array([0.5, 0.5])
    obs3.Xgrid = array([1.2, 1.6])
    obs3.Ygrid = array([1.4, 1.8])
    obs3.Zgrid = array([5.2, 5.4])
    obs3.time =  array([15782.5, 15782.5] )
    obs3 = pyromsobs.utils.setDimensions(obs3)

    obs_dict = {'value': 6, 'type': 3, 'error': 0.4, 'Xgrid': 10, 'Ygrid': 15, 'Zgrid': 35.2, 'time': 15782.0, 'provenance': 10}
    obs = pyromsobs.OBSstruct()

    obs.put(obs_dict, fill_value = -99999)
    obs3.put(obs_dict, fill_value = -99999)

    obs1 = obs3[0]
    obs2 = obs3[-1]
    obs4 = obs3[where(obs3.type == 6)]

    assert obs1.Ndatum == 1
    assert obs2.Ndatum == 1
    assert obs4.Ndatum == 2

    assert obs1.value == obs3.value[0]
    assert obs2.value == obs3.value[-1]
    assert all(isin(obs4.value, obs3.value[where(obs3.type == 6)]))

def test_adjust_survey():

    import pyromsobs
    import numpy as np
    from datetime import datetime, timedelta
    reftime = datetime(1970,1,1)

    today = datetime.now()

    obs1 = pyromsobs.OBSstruct()
    obs1.value = np.array([5.])
    obs1.type = np.array([6])
    obs1.error = np.array([0.5])
    obs1.lat = np.array([65.5])
    obs1.lon = np.array([4])
    obs1.depth = np.array([-10])
    obs1.time =  np.array([(today - reftime).total_seconds()/86400.]) # Today in fractional days since reftime
    obs1 = pyromsobs.utils.setDimensions(obs1) # This function will set Nsurvey, survey_time, and Nobs.


    # Let's use obs1 to create a timeseries with temperature observations every five minutes:
    now = datetime.now()
    now = datetime(now.year, now.month, now.day, now.hour)
    newtime = datetime(now.year, now.month, now.day, now.hour)

    # reset the time of obs1 to now
    obs1.time[:] = (now - reftime).total_seconds()/86400.
    # Create a copy of obs1:
    obs = pyromsobs.OBSstruct(obs1)

    while newtime <= now + timedelta(hours = 1):
        newtime += timedelta(minutes = 5) # update now

        # change the time
        obs.time[:] = (newtime - reftime).total_seconds()/86400.

        # Add the observation to obs1:
        obs1.append(obs)
        # Also add a duplicate every 15 minutes:
        #if not np.mod(newtime.minute, 15):  # returns zero if it can be devided by 15
        #    obs1.append(obs)


    obs1 = pyromsobs.utils.setDimensions(obs1)

    print(obs1.time, len(np.unique(obs1.time)))
    obs1 = pyromsobs.adjust_survey(obs1, dt = 1./4.)
    print(obs1.time, len(np.unique(obs1.time)))
    print(obs1.survey_time)
    assert obs1.Nsurvey == 5 # hour:00, hour:15, hour:30, hour:45, hour+1:00
    assert not all([np.mod((reftime + timedelta(days = t)).minute, 15) for t in obs1.time ])
