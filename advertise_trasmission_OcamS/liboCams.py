#-*- coding: utf-8 -*-
#! /usr/bin/env python2

import os
import v4l2
import fcntl
import mmap
import time

def xioctl(fd, request, arg):
  for i in range(10):
      r = fcntl.ioctl(fd, request, arg)
      if r == 0:
        return r
      else:
        print 'ioctrl error????', r
  return r

class buffer_struct:
    start  = 0
    length = 0

class v4l2_util():
  def __init__(self, devpath, verbose=False):
    self.verbose = verbose
    self.shape = None

    try:
      self.vd = open(devpath, 'r+')
    except:
      raise IOError('Device Open Error %s'%devpath)
    if self.verbose:
      print '--Device Open Success!!!'
      print '  + Device:', self.vd
        
    self.card = self.Capability()
    form, stp = self.GetCurrentFormat()
      
  def Close(self):
    self.vd.close()
    if self.verbose:
      print '--Device Closed',  self.vd

  def Capability(self):
    cp = v4l2.v4l2_capability()
    xioctl(self.vd, v4l2.VIDIOC_QUERYCAP, cp)
    if self.verbose :
      print '--Capability '
      print '  + driver:', cp.driver
      print '  + card:', cp.card
      print '  + bus info:', cp.bus_info
      print '  + VIDEO_CAPture:', hex(cp.capabilities&v4l2.V4L2_CAP_VIDEO_CAPTURE)
      print '  + STREAMING', hex(cp.capabilities&v4l2.V4L2_CAP_STREAMING)
    return cp.card 

  def FormatDescript(self):
    dictFmtDiscript = dict()
    if self.verbose:
      print '--FormatDescript'
    fmt = v4l2.v4l2_fmtdesc()
    fmt.type = v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE
    for i in range(20): #while True:
      try:
        fmt.index = i
        xioctl(self.vd, v4l2.VIDIOC_ENUM_FMT, fmt)
      except:
        break
      if self.verbose:
        print '  + Description:', fmt.description
        print '  + PixelFormat:', hex(fmt.pixelformat)
      dictFmtDiscript[fmt.description] = fmt.pixelformat
    return dictFmtDiscript

  def EnumerateFormats(self):
    fmtdesc = self.FormatDescript()    
    self.listValidFormats = list()
    for key in fmtdesc:
      fse = v4l2.v4l2_frmsizeenum()
      for i in range(10):
        fse.index = i
        fse.pixel_format = fmtdesc[key]
        try:
          xioctl(self.vd, v4l2.VIDIOC_ENUM_FRAMESIZES, fse)
        except:
          break
        fpslist = self.GetFrameRate(fse.pixel_format, fse.discrete.width, fse.discrete.height)
        for fps in fpslist:
          self.listValidFormats.append((key, fse.discrete.width, fse.discrete.height, fps))
        
    return self.listValidFormats

  def GetFrameRate(self, pixelformat, width, height):
    frmival = v4l2.v4l2_frmivalenum()
    
    frmival.pixel_format = pixelformat
    frmival.width = width
    frmival.height = height

    fps_list = list()
    for i in range(10):
      frmival.index = i
      try:
        xioctl(self.vd, v4l2.VIDIOC_ENUM_FRAMEINTERVALS, frmival)
      except:
        break
      if frmival.type == v4l2.V4L2_FRMIVAL_TYPE_DISCRETE :
        fps = int(1.0/(float(frmival.discrete.numerator)/float(frmival.discrete.denominator)))
        fps_list.append(fps)
      elif frmival.type == v4l2.V4L2_FRMIVAL_TYPE_CONTINUOUS:
        print 'todo V4L2_FRMIVAL_TYPE_CONTINUOUS'
      elif frmival.type == v4l2.V4L2_FRMIVAL_TYPE_STEPWISE:
        print 'todo V4L2_FRMIVAL_TYPE_STEPWISE'
      else:
        print 'todo V4L2_FRMIVAL_TYPE_*'
    return fps_list

  def EnumerateControls(self):
    self.dictValidControls = dict()
    qc = v4l2.v4l2_queryctrl()
    qc.id = v4l2.V4L2_CTRL_CLASS_USER | v4l2.V4L2_CTRL_FLAG_NEXT_CTRL
    if self.verbose:
      print '--EnumerateControls'
    for i in range(20): #while True:
      try:
        xioctl(self.vd, v4l2.VIDIOC_QUERYCTRL, qc)
      except:
        break
      if self.verbose:
        print '  +',i,':', qc.id, qc.name, qc.type, qc.flags

      if qc.flags == v4l2.V4L2_CTRL_FLAG_DISABLED :
        continue
      if qc.type == v4l2.V4L2_CTRL_TYPE_MENU :
        print 'sdkim Todo enumerate_control_menu() '
      self.dictValidControls[qc.name] = qc.id
      qc.id |= v4l2.V4L2_CTRL_FLAG_NEXT_CTRL
    return self.dictValidControls

  def GetControlValue(self, qcid):
    ctrl = v4l2.v4l2_control()
    ctrl.id = qcid
    xioctl(self.vd, v4l2.VIDIOC_G_CTRL, ctrl)
    if self.verbose:
      print '--GetControl'
      print ' + ID:', ctrl.id
      print ' + Value:', ctrl.value    
    return ctrl.value
  
  def SetControlValue(self, qcid, val):
    ctrl = v4l2.v4l2_control()
    ctrl.id = qcid
    ctrl.value = val
    xioctl(self.vd, v4l2.VIDIOC_S_CTRL, ctrl)
    if self.verbose:
      print '--SetControlValue'
      print ' + ID:', ctrl.id
      print ' + Value:', ctrl.value    

  def Set(self, fmt):
    #print 'TRY:', fmt
    (fmt, w, h, fps) = fmt
    form, stp = self.GetCurrentFormat()
    form.fmt.pix.width = w
    form.fmt.pix.height = h
    stp.parm.capture.timeperframe.denominator = fps
    stp.parm.capture.timeperframe.numerator = 1
    self.SetFormat(form, stp)
    return
    
  def SetFormat(self, form, stp ):
    xioctl(self.vd, v4l2.VIDIOC_S_FMT, form)
    self.shape = (form.fmt.pix.height, form.fmt.pix.width)
    xioctl(self.vd, v4l2.VIDIOC_S_PARM, stp)
    self.fps = stp.parm.capture.timeperframe.denominator/stp.parm.capture.timeperframe.numerator    
    if self.verbose:
      print '--SetFormat'
      print '  + set width:', form.fmt.pix.width
      print '  + set height:', form.fmt.pix.height
    #print 'Set:', self.shape, self.fps
    
  def GetCurrentFormat(self):
    form = v4l2.v4l2_format()
    form.type = v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE
    xioctl(self.vd, v4l2.VIDIOC_G_FMT, form)
    
    self.shape = (form.fmt.pix.height, form.fmt.pix.width) ##### self.shape
    
    stp = v4l2.v4l2_streamparm()
    stp.type = v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE
    xioctl(self.vd, v4l2.VIDIOC_G_PARM, stp)
    self.fps = stp.parm.capture.timeperframe.denominator/stp.parm.capture.timeperframe.numerator    
    if self.verbose:
      print '--GetCurrentFormat'
      print '  + width:', form.fmt.pix.width
      print '  + height:', form.fmt.pix.height
      print '  + pixelformat:', hex(form.fmt.pix.pixelformat)
      print '  + sizeimage:', form.fmt.pix.sizeimage
    #print 'Get:', self.shape, self.fps
    return form, stp

  def Start(self, buff_num):
    if self.verbose:
      print '==== START ===='
    req = v4l2.v4l2_requestbuffers()
    req.count  = buff_num
    req.type   = v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE
    req.memory = v4l2.V4L2_MEMORY_MMAP
    xioctl(self.vd, v4l2.VIDIOC_REQBUFS, req)

    if self.verbose:
      print '--requesetbuffers success'
      
    n_buffers = req.count
    self.buffers = list()
    for i in range(n_buffers):
      self.buffers.append( buffer_struct() )

    for i in range(n_buffers):
      buf = v4l2.v4l2_buffer()
      buf.type      = v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE
      buf.memory    = v4l2.V4L2_MEMORY_MMAP
      buf.index     = i
      xioctl(self.vd, v4l2.VIDIOC_QUERYBUF, buf)
      self.buffers[i].length = buf.length
      self.buffers[i].start = mmap.mmap(self.vd.fileno(), buf.length,
                    flags = mmap.MAP_SHARED,
                    prot  = mmap.PROT_READ|mmap.PROT_WRITE,
                    offset = buf.m.offset)
      if self.verbose:
        print '--Memory MAP'
        print '  +MMAP:', i, buf.m.offset, buf.length
      
    for i in range(n_buffers):
      buf = v4l2.v4l2_buffer()
      buf.type      = v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE
      buf.memory    = v4l2.V4L2_MEMORY_MMAP
      buf.index     = i
      xioctl(self.vd, v4l2.VIDIOC_QBUF, buf)

    if self.verbose:
      print '--requesetbuffers success'

    buftype = v4l2.v4l2_buf_type(v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE)
    xioctl(self.vd, v4l2.VIDIOC_STREAMON, buftype)

    time.sleep(1)
    buftype = v4l2.v4l2_buf_type(v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE)
    xioctl(self.vd, v4l2.VIDIOC_STREAMON, buftype)
    if self.verbose:
      print '**** START ****'
      
  def Stop(self):      
    buftype = v4l2.v4l2_buf_type(v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE)
    xioctl(self.vd, v4l2.VIDIOC_STREAMOFF, buftype)
    for buf_st in self.buffers:
      buf_st.start.close()
    if self.verbose:
      print '**** STOP ****'
    
  def GetFrame(self):
    start_time = time.time()
    buf = v4l2.v4l2_buffer()
    buf.type = v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE
    buf.memory = v4l2.V4L2_MEMORY_MMAP
    ret = xioctl(self.vd, v4l2.VIDIOC_DQBUF, buf)
    
    buf_st = self.buffers[buf.index]
    buff = buf_st.start.read(buf_st.length)
    buf_st.start.seek(0)
    xioctl(self.vd, v4l2.VIDIOC_QBUF, buf)
    if self.verbose:
      print '# GetFrame:{0:.2f}ms'.format((time.time()-start_time)*1000)

    return buff

import numpy as np
import time

class oCams():
  def __init__(self, dev, verbose=0):
    self.dev = dev
    self.cam = None
    self.verbose = verbose

    self.Print(dev,1)
    self.cam = v4l2_util(dev)
    self.Print(self.cam.card,1)
    
    if self.cam.card == 'oCamS-1CGN-U':
      self.mode = 0
    elif self.cam.card == 'oCam-5CRO-U':
      self.mode = 1
    elif self.cam.card == 'oCam-1CGN-U':
      self.mode = 2
    elif self.cam.card == 'oCam-1MGN-U':
      self.mode = 2
    elif self.cam.card == 'oCamStereo-K':
      self.mode = 3
    else:
      self.mode = 1

    self.running = False
  
  def Set(self, fmtdata):
    self.cam.Set(fmtdata)

  def GetName(self):
    return self.cam.card
  
  def Print(self, msg, level):
    if level <= self.verbose:
      print msg
    
  def Start(self):
    self.running = True
    self.cam.Start(1)

  def GetFrame(self, mode=0):
    buff = self.cam.GetFrame()
    
    if self.mode == 0:
      img = np.ndarray((self.cam.shape[0],self.cam.shape[1], 2),
                       buffer = buff, dtype=np.uint8)
      right, left  = img[:,:,0], img[:,:,1]
      if mode == 1:
        return np.hstack((left,right))
      elif mode == 2:
        return left
      elif mode == 3:
        return right

    elif self.mode == 1:
      return np.ndarray((self.cam.shape[0],self.cam.shape[1], 2),
                       buffer = buff, dtype=np.uint8)
    elif self.mode == 2:
      return np.ndarray((self.cam.shape[0],self.cam.shape[1], 1),
                        buffer = buff, dtype=np.uint8)
    elif self.mode == 3:
      return np.ndarray((self.cam.shape[0],self.cam.shape[1]*2, 1),
                        buffer = buff, dtype=np.uint8)
    else:
      return np.ndarray((self.cam.shape[0],self.cam.shape[1], 2),
                       buffer = buff, dtype=np.uint8)

  def Stop(self):
    if self.running is True:
      self.cam.Stop()
      self.running = False

  def Close(self):
    self.Stop()
    self.cam.Close()

  def GetControlList(self):
    return self.cam.EnumerateControls()
      
  def SetControl(self, ctrl_id, ctrl_val):
    return self.cam.SetControlValue(ctrl_id, ctrl_val)

  def GetControl(self, ctrl_id):
    return self.cam.GetControlValue(ctrl_id)

  def GetFormatList(self):
    return self.cam.EnumerateFormats()
    
def FindCamera(strCamera):
  import os
  try:
    for path in os.listdir('/dev/v4l/by-id/'):
      if path.find(strCamera) >= 0:
        devpath = os.path.join('/dev/v4l/by-id/',path)
        return devpath
  except OSError as Err:
    print 'Device Not Found!! Check Connection'
  return None



  
